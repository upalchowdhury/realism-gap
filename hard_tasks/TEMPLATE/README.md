# <task name>

**Family:** software engineering | ML | data engineering
**Estimated human time:** <n> h (see `baseline.md` for the measured number)
**Status:** draft | QA'd | baselined | released

## Task statement (what the agent sees)

<Exactly the text the agent receives. Nothing more. If it isn't in this section, the
agent doesn't get it. Write it the way a competent new hire would receive it: goal,
constraints, definition of done, where things are.>

## Environment

- Container: `Dockerfile` in this folder (pinned base image, pinned dependencies)
- Provided to the agent: `<paths>`
- Withheld from the agent: `tests_hidden/`, `scorer.py`, `solution/`

## Scoring

Automatic, hidden, binary unless stated. `scorer.py` runs after the agent finishes and
returns `{"score": 0|1, "partial": {...}, "notes": "..."}`. Partial credit, if any, must be
defined *before* the first model run and never adjusted afterwards.

## Why this task is hard (and stays hard)

<Which part of the task can't be shortcut by pattern-matching? What has to be understood
end-to-end? Why can't it be split into independent sub-problems and parallelized?>

## Known ambiguities

See `qa_log.md`. Every ambiguity found during QA is either resolved in the task statement
or deliberately left in with a note on how it's scored.
