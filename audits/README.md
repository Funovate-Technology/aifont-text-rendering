# Native review batches

Each folder is one batch from [aifont.ai/native-review](https://aifont.ai/native-review).

- `items.csv`: the images in the batch, in the order reviewers see them. `record_id` is the `id` of the record in `data/generations.jsonl`.
- When a batch closes, its submitted results are added here and merged into `data/generations.jsonl` as new reviews under each reviewer's chosen credit.

A batch is never changed after it opens. Images added later go into a new batch.
