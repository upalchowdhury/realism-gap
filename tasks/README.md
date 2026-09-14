# Scenario task data

Each behavior family has a `lab.jsonl` and `wild.jsonl` file with matched `pair_id`
values. Rows must include:

`id`, `pair_id`, `behavior`, `realism`, `paraphrase`, `input`, and `target`.

`input` is either a string or a non-empty list of `{role, content}` messages. The
validator checks required fields, types, duplicate IDs, duplicate paraphrases, matched
lab/wild metadata, and hard evaluation tells in wild inputs.

The bundled `sycophancy_feedback` rows are starter plumbing fixtures. They have not
been owner-reviewed for the empirical pilot. Add new families only with matched pairs,
human review against [`docs/eval_tells_checklist.md`](../docs/eval_tells_checklist.md),
and a validation check before running a model.
