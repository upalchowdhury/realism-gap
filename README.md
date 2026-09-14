# realism-gap

**Does a frontier model behave differently when the test looks like a test?**

This benchmark measures the *realism gap*: for each behavior (sycophancy, user-directed
deception, sandbagging, reward hacking), every scenario exists as a matched pair — a
**lab** version that looks like an evaluation and a **wild** version embedded in a realistic
context with tools, history and stakes. The headline number is

```
gap_b = P(misbehave | wild_b) − P(misbehave | lab_b)     (paired bootstrap, 95% CI)
```

alongside an *awareness probe* (does the model say, or reason, that it is being tested).

## Current stage

**Shareable MVP complete; empirical pilot pending.** This repository has a tested
foundation, strict measurement contract, bounded runner/export path, and static
dashboard. It contains two starter feedback-sycophancy pairs, not a validated
benchmark. The [build and deployment plan](docs/build-plan.md)
defines the stages, completion gates, known issues, and the next bounded task.

The local foundation is verified with Python >=3.11, a locked editable install, Ruff,
pytest, validation, and both lab and wild Inspect runs with mock generation and a
deterministic offline plumbing scorer. The result contract now rejects incomplete
identities and invalid grades before analysis. The next empirical step is an owner-
reviewed local pilot; no benchmark findings are published yet.
Local continuity notes live in Git-ignored `MEMORY.md`.

## Results

No validated benchmark results are published yet. The table and dashboard remain empty
until a reviewed pilot export is available; plumbing fixtures are never presented as
model findings.

| Model | Sycophancy gap | Deception gap | Sandbagging gap | Reward-hacking gap | Awareness rate |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

Live dashboard: [GitHub Pages](https://upalchowdhury.github.io/realism-gap/) (empty
state until reviewed results exist) or open [`dashboard/index.html`](dashboard/index.html)
locally. GitHub Pages is built by [`.github/workflows/pages.yml`](.github/workflows/pages.yml)
from the same deterministic dashboard command used locally.

## Reproduce the MVP

These commands require Python >=3.11. See [`docs/reproducibility.md`](docs/reproducibility.md)
for locked setup, checks, offline smoke runs, log export, and dashboard generation.

```bash
uv sync --locked --extra dev
make lint test validate dashboard
```

Offline smoke command without an API key:

```bash
inspect eval tasks/sycophancy_feedback/task.py -T realism=lab -T judge=mockllm/model --model mockllm/model --limit 2
```

The `judge=mockllm/model` override is required for an offline smoke run. In that mode
the task uses a named `offline_smoke` plumbing scorer because generic mock output cannot
emit the honesty judge's required grade. Real runs retain the configured judge.

## Layout

```
tasks/<family>/          one folder per behavior family; lab.jsonl and wild.jsonl side by side
examples/                safe offline manifest and batch-controller walkthrough
hard_tasks/<name>/       METR-style long-horizon tasks: spec, hidden scorer, QA log, timed human baseline
scorers/                 shared scorers (awareness probe, honesty rubric, test-based graders)
runner/                  batch runner: caching, retries, resumability, cost ledger
analysis/                paired bootstrap, awareness–gap correlation, mini time-horizon curve
docs/                    design doc, eval-tells checklist, AEF-one methodology map, decisions/, log/
dashboard/               static results page (GitHub Pages)
```

The dashboard is generated with `python -m analysis.dashboard [input.csv] [output.html]`.
It shows model/behavior gaps, paired-bootstrap intervals, pair counts, and direction
bars when an aggregated table exists; otherwise it shows the honest empty state.
Manifest execution is bounded and resumable with `python -m runner.batch`; see the
reproducibility guide for retry, timeout, dry-run, and budget-cap options.

## Planned method

Scenarios will be drafted with LLM assistance and hand-edited against the
[eval-tells checklist](docs/eval_tells_checklist.md). Every scenario carries a `pair_id`
so gaps are computed on matched pairs, never on marginal averages. Model-graded scorers
will be validated against 120 human-labeled transcripts (Cohen's κ and disagreements
will be reported). The target is five repetitions and three paraphrases per scenario,
subject to pilot cost and power estimates. Uncertainty will use scenario-cluster
paired-bootstrap 95% CIs. Negative results will receive the same prominence as positive
ones. A context gap alone does not establish evaluation awareness as its cause, and
the probe measures expressed cues, not hidden awareness.

## Status log

Weekly notes live in [`docs/log/`](docs/log/). Design decisions and the alternatives
rejected live in [`docs/decisions/`](docs/decisions/). What was AI-drafted versus
hand-verified is declared in [`docs/AI_USE.md`](docs/AI_USE.md).

## Citation

Report and citation will appear here at v1.0 (target: Nov 1, 2026).
