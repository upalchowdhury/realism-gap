# Reproducibility guide

This guide reproduces the tested software path. It does not produce a research claim
or a validated pilot result.

## Environment

Use CPython 3.11 or newer and install [`uv`](https://docs.astral.sh/uv/). From the
repository root:

```bash
uv sync --locked --extra dev
```

The lockfile records the dependency resolution, including Inspect AI and the OpenAI
compatible client used by the local Ollama adapter. Credentials are not required for
the offline checks.

## Checks

```bash
make lint       # ruff check .
make test       # pytest
make validate   # scenario pair/type/eval-tell checks
make dashboard  # writes dashboard/index.html; empty state if no results CSV exists
```

The test suite uses synthetic results and a checked-in score fixture. Those values
verify calculations and error handling; they are not model measurements.

## Offline Inspect smoke

The task's default honesty judge is a real model. For a no-credential plumbing check,
select the mock judge explicitly:

```bash
inspect eval tasks/sycophancy_feedback/task.py \
  -T realism=lab -T judge=mockllm/model --model mockllm/model --limit 2
inspect eval tasks/sycophancy_feedback/task.py \
  -T realism=wild -T judge=mockllm/model --model mockllm/model --limit 2
```

This selects `offline_smoke`, which only checks that mock output is non-empty. It must
never be converted into a behavior score.

## Local model calibration

The draft local configuration is in [`pilot_config.md`](pilot_config.md). A bounded
provider check can use an installed Ollama model, but its output is calibration-only:

```bash
inspect eval tasks/sycophancy_feedback/task.py \
  -T realism=lab -T judge=mockllm/model --model ollama/qwen3.8:27b \
  --limit 1 --max-tokens 1024 --max-connections 1 --timeout 120
```

Do not report this output. Before a pilot, review the scenario pair, choose the judge,
record the manifest, and confirm that visible completions fit the declared bound.

## Export and analysis

After a real run, dump each Inspect `.eval` file to JSON and combine lab and wild logs
with `runner.export.records_from_logs`. It requires exact `C`/`I` values from the
configured grader and validates all pair, seed, and paraphrase identities. Then use
`analysis.gap.gap_table` and generate the dashboard from the resulting aggregate CSV.
Do not bypass these checks by editing a CSV manually.
