# Text in AI images: did the model spell it right?

Every image we generate for **[aifont.ai](https://aifont.ai)** is checked letter by letter against the word the prompt asked for. This repo is that ledger: one record per image, with the prompt, the model, the word it was meant to write, and whether it wrote it.

<!-- stats -->
```
 2,495   images, each with a text verdict
    66   lettering styles
     8   languages
     5   image models
   733   also reviewed by a person
    74   disputed, waiting for a native speaker
```

Correct / judged, first attempts only:

| Language | GPT Image | Nano Banana | Grok Imagine | Seedream | Qwen-Image |
|---|---:|---:|---:|---:|---:|
| English | 81/82 | 64/64 | 64/65 | 64/64 | 63/64 |
| German | 63/63 | 62/62 | 61/62 | 60/62 | 61/62 |
| Spanish | 63/63 | 62/62 | 61/62 | 61/63 | 52/62 |
| Portuguese | 62/62 | 61/61 | 59/61 | 61/61 | 52/61 |
| Chinese (Simplified) | 65/65 | 62/63 | 63/64 | 61/64 | 63/64 |
| Chinese (Traditional) | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| Japanese | 65/66 | 63/64 | 56/65 | 55/65 | 48/65 |
| Arabic | 60/65 | 64/64 | 39/61 | 34/62 | 8/69 |
<!-- /stats -->

## What a record looks like

```json
{
  "id": 2172,
  "style": "witch-font",
  "language": "en",
  "target_text": "Potion",
  "model": "Qwen-Image",
  "model_id": "qwen-image-3.0-pro",
  "generated_at": "2026-10-28T17:05:33Z",
  "attempt": "first",
  "image_url": "https://cos.aifont.ai/research/attempts/witch-font/witch-font-en-qwen3pro-s1-92438.jpg",
  "gallery_id": 92438,
  "text_verdict": "correct",
  "error_types": [],
  "rendered_text": null,
  "reviews": [
    { "reviewer": "ai", "text_verdict": "correct", "native_speaker": false, "zoomed": false },
    { "reviewer": "maintainer", "text_verdict": "correct", "native_speaker": false, "zoomed": true }
  ],
  "human_reviewed": true,
  "disputed": false
}
```

Field by field in [SCHEMA.md](SCHEMA.md). The prompt text is in `data/prompts.jsonl`, keyed by `prompt_hash`.

## How the images were made

- Each lettering style has one prompt per language, written in that language, with a word in that language. The same prompt goes unchanged to every model.
- Five models, called through the same service, at one fixed resolution and quality per model. `model_id` is the upstream model version at the moment of generation, read from the service's configuration, so a silent model swap shows up as a new id.
- Nothing is edited, retouched or cherry-picked. Failed images stay in the ledger. When an image was wrong we usually generated it once more; that second image is marked `"attempt": "retry"`.

## How the text was judged

- `correct` means every letter, stroke, dot and diacritic matches `target_text`. Upper or lower case alone does not make it wrong unless the prompt asked for one.
- `incorrect` records what kind of mistake it was (`error_types`) and, for spelling mistakes, what the image actually says (`rendered_text`).
- Every image was first judged by an AI assistant. A person then went through the ones most likely to be misjudged: every image the AI marked wrong or unsure, every Arabic image, CJK images the AI had only seen on a contact sheet, plus a random sample of the rest. The sample of 50 matched the AI on all 50, so the other AI-only verdicts are kept, with `human_reviewed: false`.
- That person was not a native speaker of most of these languages. Where the AI and the person disagree on Arabic, neither is a native reader, so the record is `unsure` with `disputed: true`. Those are left out of the accuracy table.
- `reviews` lists each reviewer's own call, so you can weigh them yourself. This is not a 100% verified ground truth, and it isn't presented as one.

## Help fix it

If you read one of these languages and an image is judged wrong, open an issue with the record `id` and what the image actually says ("Wrong verdict" template). Native speakers are what this dataset needs most, Arabic first. Accepted corrections are added as a new review under your GitHub handle, and the next release recomputes the verdict.

## Counting accuracy

Use first attempts only (`"attempt": "first"`). Retries exist because the first try failed, and extra samples were drawn after a correct one, so both lean toward correct. `data/summary.json` is already filtered that way. With a few dozen images per cell, report counts, not percentages.

## Files

| File | |
|---|---|
| `data/generations.jsonl` | One record per image |
| `data/generations.csv` | Same, flattened, without prompts |
| `data/prompts.jsonl` | Prompt text by hash |
| `data/summary.json` | Correct / incorrect by model × language, first attempts |

Images are linked, not included. `gallery_id` is the image's public page on FontVibe, the service that generated it.

## License

Data: [CC BY 4.0](LICENSE). Credit "AIFont (aifont.ai)". Code in `scripts/`: MIT. See [NOTICE](NOTICE).

## Citing

See [CITATION.cff](CITATION.cff), or GitHub's "Cite this repository" button.
