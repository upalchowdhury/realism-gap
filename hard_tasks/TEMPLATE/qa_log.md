# QA log — <task name>

Checklist (all must be ticked before a model sees the task):

- [ ] I solved the task end-to-end from the agent's starting state, using only the task statement
- [ ] The hidden scorer accepted my solution
- [ ] The hidden scorer rejected at least two plausible *wrong* solutions I wrote deliberately
- [ ] No file the agent can read contains the answer, the tests, or hints (grep'd for it)
- [ ] The task statement contains everything needed; I had to look up nothing outside it
- [ ] The task cannot be split into independent pieces and parallelized
- [ ] Dependencies and base image are pinned; a fresh container builds deterministically
- [ ] A second person read the statement cold and listed their questions (below)

## Ambiguities found

| # | Found by | Ambiguity | Resolution | Date |
|---|---|---|---|---|
| 1 | | | resolved in statement / left in, scored as ... | |

## Plausible wrong solutions the scorer must reject

| # | Description | Scorer result |
|---|---|---|
| 1 | | rejected ✓ |
| 2 | | rejected ✓ |
