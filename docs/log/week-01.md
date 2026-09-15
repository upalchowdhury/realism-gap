# Week 1 — Sep 14–20, 2026

## Completed: stage 0, goal and baseline review

- Inventoried the delivered skeleton: two feedback-sycophancy pairs, Inspect task,
  awareness and honesty scorers, scenario validator, paired-bootstrap analysis,
  three tests, CI configuration, hard-task templates, and dashboard placeholder.
- Added `docs/build-plan.md` with measurement limits, build stages, completion gates,
  and deployment milestones. The next build is stage 1, the runnable foundation.
- Added project workflow guidance and ignored local memory; initialized the project
  as its own Git repository for the first local baseline commit.
- Corrected documentation that implied reproduction, human review, or a statistical
  power calculation had already happened.

## Checks performed on 2026-09-14

| Check | Result |
|---|---|
| `python3 -m runner.validate tasks/` | Passed: zero reported problems |
| Three existing test functions, invoked directly | All passed: synthetic positive gap, synthetic null interval, bundled scenario validation |
| Compile all Python sources without executing them | Passed |
| Full pytest / Ruff / Inspect smoke | Not run: tools absent from default Python environment; Python 3.9.6 is below declared >=3.11 requirement |

These checks validate only parts of the starter code. They do not establish a working
Inspect installation, hosted CI, real-model performance, or judge validity.

## Findings and open questions

- The supposed offline smoke configuration leaves a real Anthropic judge selected.
- Existing context pairs vary persona, history and pressure together. A measured
  gap would not by itself isolate evaluation awareness.
- Export/scoring semantics and exact repetition matching need to be defined before
  real results can safely enter the analysis.
- No external evaluation reproduction or paid model run has been performed.

## Completed: stage 1, runnable foundation

- Added explicit setuptools build configuration and `uv.lock`; editable installation
  now succeeds under CPython 3.11.15.
- Updated CI and Makefile to run both `lab` and `wild` with mock generation and an
  explicit mock judge argument.
- Added `offline_smoke`, a named deterministic plumbing scorer. It checks non-empty
  mock output only and is never a behavior label.
- Fixed two Ruff 0.16 findings in the existing analysis and hard-task template.
- Foundation checks passed: Ruff, pytest (3 passed), scenario validation, and both
  Inspect smoke runs. Each run completed 2/2 samples for `offline_smoke` and
  `awareness_probe`, with success status and the expected realism metadata.
- The first smoke attempt produced NaN/unscored honesty grades; that failure led to
  the explicit offline scorer rather than being hidden as a passing result.

## Next bounded step

Stage 1 is complete. Next, define score conversion and strict pair/repetition identity
checks before any result is interpreted or real model is run.

## Completed: stage 2, measurement contract

- Added `analysis/results.py`: exact `C`/`I` conversion, validated result identities,
  and score-record conversion into analyzable rows.
- Updated `paired_gap` to reject incomplete or duplicated identities instead of
  silently dropping them.
- Strengthened scenario validation for duplicate IDs, types, empty values, matching
  paraphrase sets, and matching behavior metadata.
- Added a deterministic CSV score fixture and tests for the expected gap, invalid
  grades, unmatched results, duplicate results, and malformed scenario pairs.
- Added decision record `docs/decisions/0002-result-contract.md`.
- Checks passed: Ruff, pytest (7 passed), and scenario validation.

Stage 2 is complete. No real model run, human scenario review, or benchmark result has
been produced. The next bounded milestone is stage 3, a small owner-reviewed pilot.

## Shareable MVP publication layer

- Added `analysis.dashboard`, a self-contained static renderer for aggregate gap
  tables. It shows paired-bootstrap intervals and direction bars when reviewed data
  exists, and an explicit empty state otherwise.
- Added a GitHub Pages workflow plus Makefile/CI targets so the same dashboard build
  can be checked locally and published from `main`.
- Added reproducibility and task-schema guides. They document locked setup, offline
  smoke commands, the Inspect-log export path, and the boundary between plumbing
  fixtures and benchmark evidence.
- Checks passed: Ruff, pytest (14 passed), scenario validation, and deterministic
  empty-state dashboard generation. No empirical score or public finding was added.

## Resumable batch controller

- Added `runner.batch`, which executes exact `RunSpec` commands with atomic state
  writes, skip-on-success resume behavior, bounded retries, timeout handling, dry-run
  planning, and an explicit per-attempt budget cap.
- Added tests for retry/resume, dry-run planning, and budget blocking. The controller
  stores execution metadata only; log export and result validation remain mandatory.
- Added `examples/offline_manifest.json` and its walkthrough so a fresh checkout can
  preview or execute the bounded mock lab/wild commands without credentials.
- Added `analysis.publish`, which validates long-format exports, writes the aggregate
  gap table, and rebuilds the dashboard as one deterministic publication step.

## Local model inventory and provider smoke (stage 3 preparation)

- Ollama reports: `qwen3.8:27b` (17 GB), `orcarouter/Qwen3.8-27B-Uncensored:latest`
  (17 GB), `muse-glimmer:30b-mlx` (21 GB), `gemma4:latest` (9.6 GB), and
  `qwen2.5:72b-instruct` (47 GB). Hugging Face cache reports complete local
  checkpoints for Qwen2.5 0.5B/1.5B/7B, Phi-3 Mini, and Olmo-3 7B; Kimi-K3 and
  GLM-5.2 entries are metadata only.
- Direct `ollama run qwen3.8:27b 'Respond with exactly READY.'` succeeded. A bounded
  Inspect smoke reached `ollama/qwen3.8:27b` for both lab and wild with successful
  one-sample runs. Small caps ended during hidden reasoning, leaving empty visible
  completion; these runs are provider evidence only and were discarded.
- `gemma4:latest` showed the same reasoning-cap behavior through Inspect. Direct
  Ollama `--think=false` works, but the tested Inspect OpenAI-compatible path did not
  disable thinking via `extra_body`. Stage 3 must resolve and record this setting or
  use a sufficiently bounded policy before collecting pilot results.
- The first pilot candidate is `ollama/qwen3.8:27b`; `gemma4:latest` is a possible
  second model or local judge after calibration. No benchmark scores were recorded.

## Pilot control layer

- Added `runner/manifest.py` with typed `RunSpec` bounds and deterministic command /
  manifest serialization. This prepares controlled execution without running a
  batch or writing results.
- Added `docs/pilot_config.md` with the provisional model candidates, reasoning/token
  calibration requirement, cost/configuration fields, and owner-review gate.
- Added tests for exact command construction, manifest serialization, and invalid
  bounds. The suite now passes 9 tests.

## Log export path

- Added `runner/export.py` to convert Inspect JSON log dumps into the validated
  analysis table. It carries model, behavior, pair, realism, seed, and paraphrase
  metadata; accepts only exact `C`/`I` values from the configured grader; and rejects
  missing or unscored samples before combining lab and wild logs.
- Added synthetic log tests for successful export and unscored-grade rejection. The
  suite now passes 11 tests.
