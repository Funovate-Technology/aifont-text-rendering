#!/usr/bin/env python3
"""
build_dataset.py — export the AIFont generation ledger into the public dataset files.

Reads the production ledger (gen_attempts + gen_reviews) and writes:
  data/generations.jsonl   one record per successful generation (schema: SCHEMA.md)
  data/generations.csv     the same, flattened, without the prompt text
  data/prompts.jsonl       one record per distinct prompt (prompt_hash -> text)
  data/summary.json        accuracy by model x language (first attempts only)
and refreshes the numbers between the <!-- stats --> markers in README.md.

Run from the AIFont workspace (needs ssh access to the production host):
  python3 scripts/build_dataset.py

The ledger is the source of truth; this repo is a snapshot of it. Rules:
  - Only successful generations (ok = 1). Failed API calls have no image.
  - The latest review of each image wins (reviews are append-only; a re-review supersedes).
  - Premium styles (ai_fonts.tier = 2) keep their prompt hash but not the prompt text:
    on aifont.ai the premium part of those prompts is shown only after unlocking.
  - Images are linked, not shipped. image_url points at the archived original.
"""
import collections
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HOST = "jacktu@43.130.47.235"
SSH = ["ssh", "-p", "8322", "-o", "ConnectTimeout=15", "-o", "ControlPath=none", "-o", "ControlMaster=no", HOST]
DB = "cd /app/project/aifont-prod && P=$(cat .dbpass) && docker exec -i -e MYSQL_PWD=$P mysql-8.0.45 mysql --default-character-set=utf8mb4 -uaifont aifont_prod -N -B --raw"

PURPOSE = {1: "published", 2: "language_test", 3: "word_check", 4: "pilot", 5: "control"}
KIND = {1: "first", 2: "retry", 3: "extra_sample"}
VERDICT = {1: "correct", 2: "incorrect", 3: "unsure"}
LANG = {"en": "English", "de": "German", "es": "Spanish", "pt": "Portuguese", "zh": "Chinese (Simplified)",
        "zh-hant": "Chinese (Traditional)", "ja": "Japanese", "ar": "Arabic"}
AI_REVIEWERS = {"皮皮虾", "claude"}   # the ledger's names for the AI assistant that reviewed before the human pass
MAINTAINERS = {"Jack"}                # AIFont maintainers; contributors added later appear under their own handle


def query(sql):
    """Run SQL on the server and return rows of JSON. Built server-side: the link to the host is slow."""
    p = subprocess.run(SSH + [DB], input=sql, capture_output=True, text=True, timeout=1800)
    if p.returncode:
        raise RuntimeError(p.stderr.strip())
    out = p.stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def fetch():
    attempts = query("""SELECT JSON_OBJECT('id', a.id, 'style', a.font_id, 'purpose', a.purpose, 'language', a.locale, 'text', a.word,
        'prompt_hash', a.prompt_hash, 'kind', a.attempt_kind, 'sample', a.sample, 'model', a.model_name, 'model_id', a.model_id,
        'resolution', a.resolution, 'quality', a.render_quality, 'ratio', a.ratio, 'gallery_id', a.fv_generation_id,
        'image_url', a.archive_url, 'generated_at', DATE_FORMAT(a.gen_time, '%Y-%m-%dT%H:%i:%sZ'),
        'tier', f.tier, 'live', f.status)
      FROM gen_attempts a LEFT JOIN ai_fonts f ON f.font_id = a.font_id AND f.deleted = 0
      WHERE a.deleted = 0 AND a.ok = 1 ORDER BY a.id;""")
    reviews = query("""SELECT JSON_OBJECT('attempt_id', r.attempt_id, 'verdict', r.verdict, 'error_types', r.error_types,
        'rendered', r.rendered, 'observations', r.observations, 'zoomed', r.zoomed, 'reviewer', r.reviewer, 'native', r.is_native, 'detail', r.detail,
        'reviewed_at', DATE_FORMAT(r.review_time, '%Y-%m-%dT%H:%i:%sZ'))
      FROM gen_reviews r WHERE r.deleted = 0 ORDER BY r.id;""")
    prompts = query("""SELECT JSON_OBJECT('prompt_hash', prompt_hash, 'prompt', MIN(prompt_sent))
      FROM gen_attempts WHERE deleted = 0 AND ok = 1 GROUP BY prompt_hash;""")
    by_attempt = collections.defaultdict(list)
    for r in reviews:
        by_attempt[r["attempt_id"]].append(r)   # oldest first; the last one is the ledger's current conclusion
    return attempts, by_attempt, {p["prompt_hash"]: p["prompt"] for p in prompts}


def as_list(v):
    return json.loads(v) if isinstance(v, str) else (v or [])


def who(r):
    """Public label of a reviewer. Native-speaker confirmations were logged under the AI assistant's name; they came from a maintainer."""
    if r["reviewer"] in AI_REVIEWERS:
        return "maintainer" if r["native"] else "ai"
    return "maintainer" if r["reviewer"] in MAINTAINERS else r["reviewer"]


def text_verdict(r):
    spelling = [t for t in as_list(r["error_types"]) if t != "effect_drift"]
    return "correct" if r["verdict"] == 2 and not spelling else VERDICT.get(r["verdict"])


def opinions(rs):
    """Each reviewer's latest call on the text. The ledger records a dispute as 'unsure' and keeps both sides in its notes;
    here the two sides are the AI's last call before the human pass and the human's own call."""
    last = {}
    for r in rs:
        last[who(r)] = r
    out = []
    for name, r in last.items():
        v = text_verdict(r)
        if v == "unsure" and "有争议" in (r.get("detail") or ""):
            v = "incorrect" if "Jack 判写错了" in r["detail"] else "correct"   # the human side of a dispute
        out.append({"reviewer": name, "text_verdict": v, "native_speaker": bool(r["native"]), "zoomed": bool(r["zoomed"]),
                    "reviewed_at": r["reviewed_at"]})
    return out


def record(a, rs):
    r = rs[-1] if rs else None
    spelling = [t for t in as_list(r["error_types"]) if t != "effect_drift"] if r else []
    return {
        "id": a["id"],
        "style": a["style"],
        "style_url": f"https://aifont.ai/fonts/{a['style']}" if a["live"] == 1 else None,
        "language": a["language"],
        "target_text": a["text"],
        "prompt_hash": a["prompt_hash"],
        "model": a["model"],
        "model_id": a["model_id"],
        "resolution": a["resolution"],
        "quality": a["quality"],
        "aspect_ratio": a["ratio"],
        "generated_at": a["generated_at"],
        "purpose": PURPOSE.get(a["purpose"]),
        "attempt": KIND.get(a["kind"]),
        "image_url": a["image_url"],
        "gallery_id": a["gallery_id"],
        # effect_drift alone (look off, spelling right) is recorded as a failed image in the ledger but the text is correct
        "text_verdict": text_verdict(r) if r else None,
        "error_types": spelling,
        "rendered_text": r["rendered"] or None if r else None,
        "effect_drift": "effect_drift" in as_list(r["error_types"]) if r else False,
        "observations": as_list(r["observations"]) if r else [],
        "reviews": opinions(rs),
        "disputed": bool(r) and text_verdict(r) == "unsure" and "有争议" in (r.get("detail") or ""),
        "human_reviewed": any(who(x) != "ai" for x in rs),
    }


def summary(recs):
    """Accuracy of the text: first attempts, published styles, current prompt version (retries and extra samples skew toward correct)."""
    # Same prompt for every model: per style and language, only the prompt version in use now (the latest one).
    # New styles are drafted on one model first, so earlier versions would give that model extra rows.
    current = {}
    for x in recs:
        if x["purpose"] == "published":
            current[(x["style"], x["language"])] = x["prompt_hash"]   # records are in id order, so the last one wins
    cell = collections.defaultdict(lambda: collections.Counter())
    for x in recs:
        if x["attempt"] != "first" or x["purpose"] != "published" or not x["text_verdict"]:
            continue
        if x["prompt_hash"] != current[(x["style"], x["language"])]:
            continue
        cell[(x["model"], x["language"])][x["text_verdict"]] += 1
    out = []
    for (m, l), c in sorted(cell.items()):
        n = c["correct"] + c["incorrect"]
        out.append({"model": m, "language": l, "first_attempts": sum(c.values()), "correct": c["correct"], "incorrect": c["incorrect"],
                    "unsure": c["unsure"], "accuracy": round(c["correct"] / n, 4) if n else None})
    return out


def readme_table(rows, recs):
    models = ["GPT Image", "Nano Banana", "Grok Imagine", "Seedream", "Qwen-Image"]
    langs = [l for l in LANG if any(r["language"] == l for r in rows)]
    by = {(r["model"], r["language"]): r for r in rows}
    head = "| Language | " + " | ".join(models) + " |\n|---|" + "---:|" * len(models) + "\n"
    body = ""
    for l in langs:
        cells = []
        for m in models:
            r = by.get((m, l))
            cells.append(f"{r['correct']}/{r['correct'] + r['incorrect']}" if r and r["correct"] + r["incorrect"] else "–")
        body += f"| {LANG[l]} | " + " | ".join(cells) + " |\n"
    human = sum(1 for x in recs if x["human_reviewed"])
    disputed = sum(1 for x in recs if x["disputed"])
    return (f"```\n{len(recs):>6,}   images, each with a text verdict\n{len({x['style'] for x in recs}):>6,}   lettering styles\n"
            f"{len({x['language'] for x in recs}):>6,}   languages\n{len({x['model'] for x in recs}):>6,}   image models\n"
            f"{human:>6,}   also reviewed by a person\n{disputed:>6,}   disputed, waiting for a native speaker\n```\n\nCorrect / judged. First attempts with the current prompt of each published style, so every model got the same prompts:\n\n" + head + body)


def main():
    attempts, reviews, prompts = fetch()
    recs = [record(a, reviews.get(a["id"])) for a in attempts]
    premium = {a["prompt_hash"] for a in attempts if a["tier"] == 2}
    DATA.mkdir(exist_ok=True)
    (DATA / "generations.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    with open(DATA / "generations.csv", "w", newline="", encoding="utf-8") as f:
        flat = [{**{k: v for k, v in r.items() if k != "reviews"},
                 "error_types": ";".join(r["error_types"]), "observations": ";".join(r["observations"]),
                 "reviews": ";".join(f"{o['reviewer']}:{o['text_verdict']}" + (":native" if o["native_speaker"] else "") for o in r["reviews"])}
                for r in recs]
        w = csv.DictWriter(f, fieldnames=list(flat[0]))
        w.writeheader()
        w.writerows(flat)
    used = {r["prompt_hash"] for r in recs}
    (DATA / "prompts.jsonl").write_text("".join(
        json.dumps({"prompt_hash": h, "prompt": None if h in premium else prompts[h], "withheld": h in premium}, ensure_ascii=False) + "\n"
        for h in sorted(used)), encoding="utf-8")
    rows = summary(recs)
    (DATA / "summary.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme = re.sub(r"<!-- stats -->.*?<!-- /stats -->", lambda _: "<!-- stats -->\n" + readme_table(rows, recs) + "<!-- /stats -->", readme, flags=re.S)
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    human = sum(1 for x in recs if x["human_reviewed"])
    disputed = sum(1 for x in recs if x["disputed"])
    print(f"✅ {len(recs)} records, {len(used)} prompts ({len(premium & used)} withheld), {human} reviewed by a person, {disputed} disputed")


if __name__ == "__main__":
    main()
