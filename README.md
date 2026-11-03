# Text in AI images: did the model spell it right?

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23815210.svg)](https://doi.org/10.5281/zenodo.23815210)

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

Correct / judged. First attempts with the current prompt of each published style, so every model got the same prompts:

| Language | GPT Image | Nano Banana | Grok Imagine | Seedream | Qwen-Image |
|---|---:|---:|---:|---:|---:|
| English | 58/59 | 58/58 | 58/58 | 58/58 | 57/58 |
| German | 59/59 | 59/59 | 58/59 | 56/59 | 57/59 |
| Spanish | 59/59 | 59/59 | 58/59 | 57/59 | 49/59 |
| Portuguese | 59/59 | 59/59 | 55/59 | 59/59 | 50/59 |
| Chinese (Simplified) | 59/59 | 58/59 | 58/59 | 56/59 | 56/59 |
| Japanese | 59/59 | 58/59 | 52/59 | 51/59 | 45/59 |
| Arabic | 48/50 | 51/51 | 35/49 | 27/47 | 6/53 |
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

## Native review

Native speakers can also check images in batches at [aifont.ai/native-review](https://aifont.ai/native-review). Each batch covers one language. For every image you see the word the model was asked to write, but not the model name or our earlier verdict, so your call is independent. Submitted results are added to this dataset as new reviews under the credit you choose, and the accuracy table is recomputed from them. Open batches:

| Batch | Language | Images | What it covers |
|---|---|---|---|
| [AR-001](https://aifont.ai/native-review/AR-001) | Arabic | 291 | Every Arabic first attempt behind the accuracy table, including the 41 disputed ones |
| [JA-001](https://aifont.ai/native-review/JA-001) | Japanese | 295 | Every Japanese first attempt behind the accuracy table |

The image list of each batch is in [`audits/<batch>/items.csv`](audits/); results go there too once a batch closes.

## Counting accuracy

Use first attempts only (`"attempt": "first"`). Retries exist because the first try failed, and extra samples were drawn after a correct one, so both lean toward correct. To compare models, also keep to the published styles (`"purpose": "published"`) and the prompt version each style uses now: new styles were drafted on one model before all five ran. `data/summary.json` and the table above are filtered that way, and leave out disputed images. With about 60 images per cell, report counts, not percentages.

## Files

| File | |
|---|---|
| `data/generations.jsonl` | One record per image |
| `data/generations.csv` | Same, flattened, without prompts |
| `data/prompts.jsonl` | Prompt text by hash |
| `data/summary.json` | Correct / incorrect by model × language, first attempts |
| `audits/<batch>/items.csv` | Images in each native review batch |

Images are linked, not included. `gallery_id` is the image's public page on FontVibe, the service that generated it.

## License

Data: [CC BY 4.0](LICENSE). Credit "AIFont (aifont.ai)". Code in `scripts/`: MIT. See [NOTICE](NOTICE).

## Citing

DOI: [10.5281/zenodo.23815210](https://doi.org/10.5281/zenodo.23815210) (all versions). See [CITATION.cff](CITATION.cff), or GitHub's "Cite this repository" button.
