# Local pilot configuration (draft)

Status: provider calibration complete; pilot results are still unauthorized.

The first local model candidate is `ollama/qwen3.8:27b`. It is installed locally,
GPU-loaded during the provider check, and reachable through Inspect after installing
the OpenAI-compatible client. `ollama/gemma4:latest` is the current second-model or
local-judge candidate. These names are local inventory observations, not pinned
public model releases.

## Calibrated resource policy

The installed Inspect 0.3.263 Ollama wrapper does not accept provider-specific
`extra_body` or `reasoning_effort` values as `-M` model arguments. Direct Ollama
`--think=false` works, but the reproducible Inspect route is the OpenAI-compatible
endpoint with `reasoning_effort=none` in the model specification. A discarded wild
one-sample calibration produced visible text with this configuration; it is provider
evidence only, not a benchmark observation.

Record the exact Inspect version, model tag, endpoint, model options, `max_tokens`,
`timeout`, and `max_connections` in the run manifest.

The calibrated starting policy is:

```text
model=openai/qwen3.8:27b
model_base_url=http://127.0.0.1:11434/v1
reasoning_effort=none
max_tokens=768
timeout=120 seconds
max_connections=1
```

This is a starting bound, not a claim that either candidate is suitable for the
benchmark. Use `OPENAI_API_KEY=ollama` for the local endpoint. The model's output and
the calibration logs must be discarded before the review gate is passed.
`offline_smoke` may be used during calibration; it is not a behavior score.

## Review gate

Before a real score enters `analysis/results.py`, the project owner must:

1. Read every lab/wild pair and confirm the underlying decision is the same.
2. Review each wild item against `docs/eval_tells_checklist.md`.
3. Mark scenario provenance and paraphrase-0 authorship accurately.
4. Approve the judge rubric and the `C`/`I` interpretation for this behavior.
5. Approve the model/judge pair, token policy, and maximum spend.

The two starter pairs are useful plumbing fixtures but have not passed this gate.
They may be used for provider calibration only; their outputs must not be reported
as a pilot or as evidence of a realism gap.

## First executable matrix after approval

Start with one seed and paraphrase 0 on the reviewed set, run both realism sides,
and inspect transcripts and judge grades manually. Expand to additional seeds,
paraphrases, and the second model only after the first pass has complete manifests,
valid result identities, and no unresolved grading failures.

Use `runner.export.records_from_logs` to combine the lab and wild Inspect JSON log
dumps. It requires each sample's exact `model_graded_qa` value (`C` or `I`) and
passes the combined rows through the strict result contract before analysis.

The manifest runner can encode this local policy directly with `model_base_url` and
`reasoning_effort`; it inherits `OPENAI_API_KEY` from the execution environment.
