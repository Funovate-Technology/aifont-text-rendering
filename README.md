# Text in AI images: did the model spell it right?

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23815210.svg)](https://doi.org/10.5281/zenodo.23815210)

Every image we generate for **[aifont.ai](https://aifont.ai)** is checked letter by letter against the word the prompt asked for. This repo is that ledger: one record per image, with the prompt, the model, the word it was meant to write, and whether it wrote it.

<!-- stats -->
```
11,115   images
10,818   with a text verdict (AI reviewer or person)
   314   lettering styles
     8   languages
     5   image models
   753   also reviewed by a person
    40   disputed, waiting for a native speaker
```

Correct / judged. First attempts with the current prompt of each published style, so every model got the same prompts:

| Language | GPT Image | Nano Banana | Grok Imagine | Seedream | Qwen-Image |
|---|---:|---:|---:|---:|---:|
| English | 279/282 | 281/281 | 278/282 | 261/276 | 256/280 |
| German | 282/284 | 282/284 | 276/282 | 248/277 | 254/281 |
| Spanish | 281/281 | 281/282 | 273/282 | 254/277 | 243/281 |
| Portuguese | 281/282 | 282/283 | 275/282 | 261/278 | 245/281 |
| Chinese (Simplified) | 247/251 | 249/251 | 239/251 | 232/248 | 223/250 |
| Japanese | 248/250 | 243/249 | 228/249 | 214/248 | 154/250 |
| Arabic | 206/227 | 233/238 | 181/225 | 120/224 | 58/232 |
<!-- /stats -->

### AI shouldn't get your language wrong

AI has only truly practised a handful of scripts. In the others, the result often looks convincing at a glance, until you find missing strokes and letters joined the wrong way. Model makers rarely catch these mistakes themselves; native speakers spot them instantly. Every judgement you make goes into this dataset under the name you choose.

**Want to join in your language? Write to hello@aifont.ai.** See [Native review](#native-review).

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
- That person was not a native speaker of most of these languages. Every Arabic image behind the accuracy table was also reviewed by a native Arabic speaker (batch AR-001). Where a native speaker is sure, their call decides `text_verdict`. Images that are still disputed are `unsure` with `disputed: true` and left out of the accuracy table.
- `reviews` lists each reviewer's own call, so you can weigh them yourself. This is not a 100% verified ground truth, and it isn't presented as one.

## Help fix it

If you read one of these languages and an image is judged wrong, open an issue with the record `id` and what the image actually says ("Wrong verdict" template). Native speakers are what this dataset needs most, Arabic first. Accepted corrections are added as a new review under your GitHub handle, and the next release recomputes the verdict.

## Native review

AI now writes for the whole world: posters, signs, greeting cards, slides and much more. Yet it has only truly practised a handful of scripts. Switch to any other and the result often looks convincing at a glance, until you look closer and find missing strokes and letters joined the wrong way. Hundreds of millions of people speak these languages, and AI has never taken them seriously.

Model makers rarely catch these mistakes themselves; native speakers spot them instantly. So we are putting them on the table. We test one script at a time and publish every image and every judgement, with evidence clear enough that the people who build these models can see the errors, can't ignore them, and can fix them. We are starting with seven languages and will keep adding more.

This needs the eyes of native speakers. Every judgement you make speaks for everyone who shares your language: it goes into the open dataset under the name you choose to leave, so that next time AI gets your language right.

### How to take part

Every batch is listed at [aifont.ai/native-review](https://aifont.ai/native-review) in the open, for anyone to see. Invited reviewers can take any batch in their own language, and each batch is reviewed by several people separately so the answers can be checked against each other. Each answer is saved as a draft automatically, and nothing counts until you sign and submit.

Reviewing is by invitation. **Want to join in your language? Write to hello@aifont.ai.**

Each batch covers one language. For every image you see the word the model was asked to write, but not the model name or our earlier verdict, so your call is independent. Submitted results are added to this dataset as new reviews under the credit you choose; where the reviewer is sure, their call decides the verdict, and the accuracy table is recomputed. Batches:

| Batch | Language | Images | What it covers | Results |
|---|---|---|---|---|
| [AR-001](https://aifont.ai/native-review/AR-001) | Arabic | 291 | Every Arabic first attempt behind the accuracy table (v1.0.0) | [Reviewed](audits/AR-001/results.csv) by a native Arabic speaker, merged |
| [JA-001](https://aifont.ai/native-review/JA-001) | Japanese | 295 | Every Japanese first attempt behind the accuracy table (v1.0.0) | Open |
| AR-002 – AR-053 | Arabic | 1,557 | 2026-11 update: every new Arabic image in the accuracy table, then the other new ones | Open |
| JA-002 – JA-010 | Japanese | 252 | 2026-11 update: images the AI judged wrong or unsure, never checked zoomed in, plus a random spot check | Open |
| ZH-001 – ZH-006 | Chinese | 152 | Same as above, Chinese | Open |
| EN-001 – EN-002, ES-001 – ES-002, PT-001 – PT-002, DE-001 – DE-002 | English, Spanish, Portuguese, German | 191 | 2026-11 update: images the AI judged wrong or unsure, plus a random spot check | Open |

The 2026-11 batches are small on purpose: about 30 images each, roughly 10 minutes. Invited reviewers can take any open batch in their language at [aifont.ai/native-review](https://aifont.ai/native-review); the earlier batches in each language hold the images behind the accuracy table.

The image list of each batch is in [`audits/<batch>/items.csv`](audits/), submitted results in `audits/<batch>/results.csv`.

## Counting accuracy

Use first attempts only (`"attempt": "first"`). Retries exist because the first try failed, and extra samples were drawn after a correct one, so both lean toward correct. To compare models, also keep to the published styles (`"purpose": "published"`) and the prompt version each style uses now: new styles were drafted on one model before all five ran. `data/summary.json` and the table above are filtered that way, and leave out disputed images. Most verdicts so far come from an AI reviewer (see `reviews` in each record); the batches under Native review are where people check them. Report counts, not percentages.

## Files

| File | |
|---|---|
| `data/generations.jsonl` | One record per image |
| `data/generations.csv` | Same, flattened, without prompts |
| `data/prompts.jsonl` | Prompt text by hash |
| `data/summary.json` | Correct / incorrect by model × language, first attempts |
| `audits/<batch>/items.csv` | Images in each native review batch |
| `audits/<batch>/results.csv` | Submitted native review results |

Images are linked, not included. `gallery_id` is the image's public page on FontVibe, the service that generated it.

## License

Data: [CC BY 4.0](LICENSE). Credit "AIFont (aifont.ai)". Code in `scripts/`: MIT. See [NOTICE](NOTICE).

## Citing

DOI: [10.5281/zenodo.23815210](https://doi.org/10.5281/zenodo.23815210) (all versions). See [CITATION.cff](CITATION.cff), or GitHub's "Cite this repository" button.
