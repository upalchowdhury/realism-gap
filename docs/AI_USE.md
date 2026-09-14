# How AI tools are used in this project

## Work recorded so far

- The original brief says the starter repository was AI-generated on 2026-09-13,
  including the Inspect task, scenarios, scoring, analysis, tests, CI, and templates.
  It also says Inspect could not be executed in that environment.
- On 2026-09-14, the coding assistant reviewed the local skeleton, wrote the staged
  build/deployment plan, clarified incomplete work and unsupported power claims,
  added Git-ignored continuity notes, and prepared the initial local Git commit.
- The assistant ran the scenario validator, directly invoked the three existing
  test functions, and checked Python source syntax. This is not a full pytest, lint,
  or Inspect execution. See `docs/log/week-01.md` for the validation limits.
- No human-authorship, human-review, judge-validation, or timed-baseline claim is
  established for the starter scenarios by this record.
- In stage 1, the assistant added packaging configuration, a dependency lockfile,
  mock smoke plumbing, and lint fixes. The assistant executed the local foundation
  checks; the mock outputs are plumbing evidence, not benchmark findings.
- In stage 2, the assistant added the score/result contract, stricter scenario
  validation, a deterministic fixture, tests, and decision record. These tests use
  synthetic or fixture data and contain no model performance findings.
- In stage 3 preparation, the assistant queried the owner’s local Ollama/Hugging Face
  inventory and ran bounded provider-connectivity checks. The generated outputs were
  discarded; they are not benchmark observations or human labels.

## Intended division of work

AI tools may assist with code, scenario drafts, paraphrases, and literature summaries.
Record what was generated and what was subsequently reviewed. AI assistance with
design or interpretation must also be disclosed rather than described as human-only.

The project owner will supply the 120 human labels, timed human baselines, final
scenario review, and final research judgments. Paraphrase 0 is intended to be
human-authored; the starter examples need human replacement or explicit provenance
before being counted toward that requirement. Never substitute model-generated
labels or solves for these human contributions.

## Evidence to retain

Link claims to actual commits, run manifests, transcripts, label records, baseline
logs, or decision records. Mark planned artifacts as planned until they exist. Record
reviewer disagreements and unresolved anomalies instead of implying they are resolved.
