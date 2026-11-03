# Schema

One record per successful generation in `data/generations.jsonl`.

| Field | Type | Notes |
|---|---|---|
| `id` | int | Stable across releases. |
| `style` | string | Lettering style slug, e.g. `witch-font`. |
| `style_url` | string \| null | The style's page on aifont.ai; `null` for pilot and control styles that never went live. |
| `language` | string | `en` `de` `es` `pt` `zh` `zh-hant` `ja` `ar`. The prompt is written in this language. |
| `target_text` | string | The exact text the prompt asked the model to write. |
| `prompt_hash` | string | MD5 of the full prompt sent. Text in `data/prompts.jsonl`. |
| `model` | string | `GPT Image` · `Nano Banana` · `Grok Imagine` · `Seedream` · `Qwen-Image` |
| `model_id` | string | Upstream model version at generation time. |
| `resolution` / `quality` / `aspect_ratio` | string | Generation settings. |
| `generated_at` | string | UTC, ISO 8601. |
| `purpose` | string | `published` (shown on aifont.ai), `language_test`, `word_check`, `pilot`, `control`. |
| `attempt` | string | `first` · `retry` (an earlier image in the same cell was wrong) · `extra_sample` (earlier ones were right). Cell = style × language × model × prompt version. |
| `image_url` | string | Archived original, unedited. |
| `gallery_id` | int | The image's id on FontVibe, the service that generated it. |
| `text_verdict` | string | `correct` · `incorrect` · `unsure` |
| `error_types` | string[] | For `incorrect`: see below. |
| `rendered_text` | string \| null | What the image actually says, for spelling mistakes. |
| `effect_drift` | bool | The look missed the style badly enough that we regenerated. Independent of spelling. |
| `observations` | string[] | Recorded on correct images too; see below. |
| `reviews` | object[] | Each reviewer's latest call on the text: `reviewer` (`ai`, `maintainer`, a contributor's GitHub handle, or the credit a native reviewer chose), `text_verdict`, `native_speaker`, `zoomed`, `reviewed_at`; native review results also carry `batch`. |
| `human_reviewed` | bool | At least one person reviewed this image. `false` means the AI's verdict only. |
| `disputed` | bool | Reviewers disagree and none is a native speaker. `text_verdict` is then `unsure`. |

## `error_types`

| Value | Meaning |
|---|---|
| `extra_letter` | An extra letter, stroke or character |
| `missing_letter` | A letter, stroke or character left out |
| `wrong_letter` | A different letter or character, often a look-alike |
| `order` | Letters out of order, including right-to-left scripts written backwards |
| `malformed` | Shapes that can't be read as any letter |
| `joining` | Wrong Arabic joining form (initial / medial / final) |
| `dots_diacritics` | Wrong dots or marks: Arabic dots, umlauts, accents, Japanese dakuten |
| `case` | Wrong case, only where the prompt asked for upper or lower case |
| `extra_text` | Text the prompt didn't ask for, competing with the target |
| `word_split` | The word broken apart or wrapped badly |

## `observations`

`decoration_added` · `background_text` · `style_drift` · `layout_drift` · `color_drift` · `cropped` · `low_contrast`
