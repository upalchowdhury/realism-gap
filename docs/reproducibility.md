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

The complete publication step is:

```bash
python -m analysis.publish results/validated.csv results/gap_table.csv \
  dashboard/index.html --bootstrap 10000 --seed 0
```

The command refuses incomplete identities or invalid grades through the analysis
contract and writes the aggregate table and dashboard only after validation succeeds.

## Bounded batch execution

Create a JSON manifest with `runner.manifest.write_manifest`, then run it through the
resumable controller:

```bash
python -m runner.batch pilot_manifest.json \
  --state logs/batch_state.json --retry-limit 1 \
  --budget-usd 20 --cost-per-attempt-usd 0
```

The state file records each exact manifest entry, attempts, exit status, and elapsed
time. Successful entries are skipped on rerun; failures and timeouts retry only up to
the declared limit. A budget cap marks later entries `blocked_budget` rather than
starting work that would exceed it. Use `--dry-run` to materialize a plan without
executing Inspect. The controller records execution state only; failed or incomplete
runs cannot enter analysis until log export validates them.

For a no-key example, use [`examples/offline_manifest.json`](../examples/offline_manifest.json)
with the walkthrough in [`examples/README.md`](../examples/README.md). Its mock output
is plumbing and must not be reported as model behavior.
