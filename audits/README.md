# Native review batches

Each folder is one batch from [aifont.ai/native-review](https://aifont.ai/native-review).

- `items.csv`: the images in the batch, in the order reviewers see them. `record_id` is the `id` of the record in `data/generations.jsonl`.
- `results.csv`: submitted results, one row per image and reviewer. They are merged into `data/generations.jsonl` as new reviews under each reviewer's chosen credit; where a native speaker is sure, their call decides `text_verdict`.

A batch is never changed after it opens. Images added later go into a new batch.
