# Local pilot configuration (draft)

Status: preparation only. No pilot result is authorized by this file.

The first local model candidate is `ollama/qwen3.8:27b`. It is installed locally,
GPU-loaded during the provider check, and reachable through Inspect after installing
the OpenAI-compatible client. `ollama/gemma4:latest` is the current second-model or
local-judge candidate. These names are local inventory observations, not pinned
public model releases.

## Resource policy to resolve before the pilot

Both candidates emit hidden reasoning through Inspect. Small caps can end a sample
before a visible completion exists. Before collecting a score, calibration must
establish a reasoning/token setting that produces a non-empty final answer and a
bounded wall-clock cost. Record the exact Inspect version, model tag, model options,
`max_tokens`, `timeout`, and `max_connections` in the run manifest.

The tested default is deliberately conservative:

```text
max_tokens=1024
timeout=120 seconds
max_connections=1
```

It is a starting bound, not a claim that either candidate succeeds within it.
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
