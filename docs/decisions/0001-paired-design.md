# 0001 — Compute the gap on matched pairs, not marginal averages

**Date:** 2026-09-14
**Status:** accepted

## Context

The obvious design is two independent datasets, one "lab-style" and one "wild-style",
and a comparison of their misbehavior rates. This is how most realism claims in the
literature are made.

## Decision

Every scenario is authored as a pair sharing a `pair_id`, with the same underlying
decision. The gap is the mean of within-pair differences; the CI comes from bootstrapping
over pairs. `runner/validate.py` refuses unpaired scenarios.

## Alternatives rejected

- **Independent datasets.** Any difference is confounded by topic, difficulty, and length.
  A reviewer can always say "your wild set is just harder." Rejected.
- **Same prompt with a realism *wrapper* prepended.** Cheap, but the wrapper itself is a
  tell, and it doesn't add history, tools or stakes. Rejected as the main design; kept as
  an ablation (planned, week 6).

## Consequences

- Authoring is roughly 2× the work per scenario.
- Statistical power comes from pairs. The proposed ~20 pairs × 3 paraphrases × 5
  repetitions per family is a planning target, not a demonstrated ability to detect
  a 15-point gap. A power simulation is required in stage 2 before fixing the run size.
