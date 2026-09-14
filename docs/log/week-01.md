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
