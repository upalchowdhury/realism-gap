# Contributing

## Adding a scenario pair

1. Copy an existing row in `tasks/<family>/lab.jsonl`, give it a new `pair_id`.
2. Write the wild partner in `wild.jsonl` with the same `pair_id` and the same underlying decision.
3. Run `python -m runner.validate tasks/` — it must pass.
4. Walk the soft-tells table in `docs/eval_tells_checklist.md` for the wild version.
5. Open a PR with the pair and one sentence on why the decision is the same in both.

## Adding a hard task

Copy `hard_tasks/TEMPLATE/`. A task is not "done" until every box in `qa_log.md` is
ticked and `baseline.md` has at least one timed solve.

## Changing a judge rubric or scorer

Rubrics are part of the method. Any change needs a decision record in `docs/decisions/`
and re-running the judge validation set.
