#!/usr/bin/env python3
"""
merge_native_review.py — add submitted native review results to the current snapshot, without re-exporting the ledger.

build_dataset.py re-exports everything from the ledger, which also pulls in images generated after the last release.
This script only touches what native review changed:
  - reads data/generations.jsonl as it is,
  - adds every submitted native review result (aifont.ai/native-review) as a review under the reviewer's chosen credit,
  - lets a native speaker's correct / incorrect decide text_verdict (unsure leaves the earlier verdict),
  - writes audits/<batch>/results.csv and recomputes data/generations.csv, data/summary.json and the README numbers.
Records already carrying a review from the same reviewer and batch are not doubled.

Run from the AIFont workspace (needs ssh access to the production host):
  python3 scripts/merge_native_review.py
"""
import collections
import json

import build_dataset as b


def main():
    native = b.query(b.NATIVE_SQL)
    for n in native:
        n["name"] = b.credit(n)
    recs = [json.loads(line) for line in (b.DATA / "generations.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = {r["id"] for r in recs}
    missing = [n for n in native if n["attempt_id"] not in ids]
    if missing:
        raise SystemExit(f"{len(missing)} native review results point at records not in this snapshot")
    by_native = collections.defaultdict(list)
    for n in native:
        by_native[n["attempt_id"]].append(n)
    changed = 0
    for i, r in enumerate(recs):
        seen = {(o["reviewer"], o.get("batch")) for o in r["reviews"]}
        ns = [n for n in by_native.get(r["id"], ()) if (n["name"], n["batch"]) not in seen]
        if ns:
            before = r["text_verdict"]
            recs[i] = b.apply_native(r, ns)
            changed += recs[i]["text_verdict"] != before
    b.write_audit_results(native)
    b.write_outputs(recs, None, set())
    print(f"   {len(native)} native review results merged, {changed} text verdicts changed")


if __name__ == "__main__":
    main()
