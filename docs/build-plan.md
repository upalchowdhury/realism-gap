# Build and deployment plan

Updated: 2026-09-14. Current stage: **2 complete — measurement contract**. Next: **3 — small real pilot**.

This is the execution plan for the original brief in [`../doc.md`](../doc.md).
That brief records ambitions and hypotheses; it is not evidence of completed work.
Its linked Claude artifact was inaccessible during this review, so this plan uses the
files in this repository. Dates below are targets; completion gates take priority.

## Goal and boundaries

Build a reproducible behavioral benchmark that asks: **does a model's measured
misbehavior change when the same underlying decision appears in an obvious test
versus a realistic working context?**

Each scenario has a lab and wild version. For each model and behavior, average the
wild-minus-lab misbehavior difference within scenario pairs, then report the mean
difference and a 95% confidence interval by resampling scenario pairs. Repetitions
and paraphrases stay within their scenario cluster; they are not independent scenarios.
Positive gaps mean more measured misbehavior in wild contexts; negative gaps mean less.

The primary artifact is evidence that someone else can inspect and reproduce:
scenario pairs, scoring rules, run manifests, validated judgments, analysis, and a
public results page. The career/organization ambitions in the brief are downstream
uses of that evidence, not benchmark acceptance criteria.

Start with sycophantic feedback. Add factual capitulation, deception, sandbagging,
and reward hacking only after that first measurement path works. Hard software/ML
tasks are a later capability substrate for the agentic families and a separate
portfolio artifact, not a prerequisite for the first pilot.

The first useful result is **10 reviewed sycophancy pairs, run on two selected
models, with traceable scores and explicitly exploratory paired analysis**.
A zero or negative gap is a valid outcome.

## What the result can establish

- The main comparison measures sensitivity to the chosen context bundle. History,
  stakes, persona, and wording change together in the existing examples; attributing
  a gap specifically to evaluation awareness requires controlled ablations.
- The current lab examples are short feedback requests, not explicit announcements
  of evaluation. Define and review the intended lab manipulation before the pilot.
- An awareness-pattern hit measures expressed cues in available output. No hit does
  not establish lack of awareness; exposed reasoning varies across providers.
- Twenty pairs per family, eight models, five repetitions, three paraphrases,
  Cohen's kappa >= 0.75, and a full run below $400 are planning targets. Power, judge
  reliability, and cost need evidence before scale is fixed.
- Claims about novelty, external system cards, job listings, and compliance in the
  original brief remain unverified. Verify primary sources before public claims.

## Baseline inventory and review

| Area | Present now | Missing or needing verification |
|---|---|---|
| Scenarios | Two sycophancy feedback pairs, paraphrase 0 | Human provenance/review, clear lab manipulation, further scenarios |
| Inspect task | JSONL loading, generation, honesty judge, awareness regex | Supported environment install and both-realism execution |
| Scoring | C/I honesty rubric and awareness pattern matcher | Explicit `misbehaved` conversion, malformed-grade handling, human validation |
| Validation | Required fields, pair sides, regex tells | Types, duplicate IDs, matching paraphrase sets, empty datasets, system/tool text coverage |
| Analysis | Scenario-cluster bootstrap, strict result contract, and fixture tests | Statistical power simulation and robustness tables |
| Runner | Scenario validator; typed bounded `RunSpec`, manifest writer, and log exporter | Budget tracking, caching, retry/resume |
| Hard tasks | Template, hidden-scorer stub, baseline and QA sheets | First complete task, isolated scorer, genuine timed human solve |
| Publication | CI configuration, static HTML placeholder, documentation | Executed CI, reproducible artifacts, Pages deployment |

Specific findings to resolve during the next stages:

1. CI and Makefile now pass `mockllm/model` explicitly for the offline smoke path.
   Because generic mock output cannot satisfy the honesty judge's grade contract,
   the task selects a named `offline_smoke` plumbing scorer for that path. Real runs
   retain the explicit Anthropic judge. Inspect documents alternate model selection
   for scorers separately from the evaluated model: [Using Models](https://inspect.aisi.org.uk/models.html#model-api).
2. `pyproject.toml` has no explicit build backend/package discovery configuration
   despite multiple top-level packages. Test editable installation and correct it
   if needed; do not assume the setup instructions work.
3. `analysis/gap.py` drops incomplete scenario pairs and does not verify matched
   seed/paraphrase keys. Fix this before interpreting real results.
4. The task grades honesty, while analysis expects binary misbehavior. Define
   C -> 0, I -> 1, and invalid/missing -> explicit failure, never silently a zero.
5. The rubric and targets need review: e.g. the tagline target says “matter” occurs
   three times, but the quoted tagline contains “Matters” and “Matter” (two).
   Do not freeze these starter examples as human-validated ground truth.

## Stages and completion gates

Each row is a bounded milestone, potentially several small commits. Complete and
review the current milestone before moving to the next. Today stops after stage 0.

| Stage | Build scope | Evidence required to finish | Deployment boundary |
|---|---|---|---|
| **0. Goal and baseline — complete** | Audit skeleton; write this plan; add ignored local memory; initialize Git and commit baseline | Scenario validator, available baseline checks, honest record of unexecuted checks, memory absent from Git index | Local commit only; published as baseline |
| **1. Runnable foundation — complete** | Python >=3.11 environment; reproducible dependency install; fix packaging/imports and mock judge configuration; lab + wild smoke runs; align Makefile and CI | Fresh editable install from `uv.lock`; Ruff; pytest; scenario validator; both mock runs complete with 2/2 scores per scorer and matching metadata, without API keys; logs inspected | Locally runnable; CI fix ready for push |
| **2. Measurement contract — complete** | Scenario schema and pair invariants; score conversion and score export contract; strict analysis input checks; awareness naming/limitations; written design and power simulation | Deterministic fixture travels from scores to expected gap; missing/duplicate/mismatched keys and invalid grades fail visibly; decision record documents the contract | Proposed `v0.2-design` after stage evidence exists |
| **3. Small real pilot — week 2** | Grow to 10 reviewed feedback pairs; select two models and judge; cap tokens/spend; capture manifests and manual score spot-checks; run a controlled pilot | Reviewable lab/wild transcripts, complete paired export, exploratory gap/CI, actual cost, rubric disagreements and limitations; owner supplies human review | Proposed `v0.3-pilot`; publish reviewed pilot artifacts and a basic static report when requested |
| **4. Broader tasks and judge validation — weeks 3–4** | Add one family at a time; build one hard task before expanding toward four; pin containers; separate hidden tests; collect 120 human labels and timed baselines | Per-family smoke and validity checks; judge agreement with disagreements reported; hidden scorer accepts a correct solve and rejects plausible wrong solves; human baseline recorded | Draft contribution and task artifacts once independently reviewable |
| **5. Controlled scale — week 5** | Manifest-driven batches, reuse/resume, retry limits, cost ledger and stop budget; pilot-derived matrix; hard-task runner integration after verifying its current standard | Interrupted run resumes without duplicate records; all generation/judge/retry/tool costs accounted for; budget bounds tested; planned vs completed coverage recorded | Freeze run configuration, execute batch jobs, publish versioned result artifacts |
| **6. Analysis and results deployment — week 6** | Cluster-bootstrap tables, ablations, awareness associations, robustness and anomalies; time-vs-success plot if hard-task coverage supports it; three realism audits | Rebuild tables from frozen exports; uncertainty/sample counts/failures shown; nulls visible; conclusions limited to tested setup | Deploy reviewed static dashboard to GitHub Pages; retain prior artifact for rollback |
| **7. Reproducible release — weeks 7–8** | Report, methodology mapping, demo, contribution review, release manifest and reproducibility instructions | Independent rerun of documented example; every public number traces to a run and commit; ownership/provenance accurate | Proposed `v1.0-results`; release and external submissions as separately requested |

Week 1 also includes a bounded reproduction of one existing evaluation on three
models, after the offline foundation and a cost estimate. Record its task/version,
configuration, expected comparison and observed result before the proposed
`v0.1-reproduction` tag. This is separate from our own benchmark findings.

At the end of week 4, review the brief's kill criterion. Consistently small gaps
and absent awareness cues should trigger a review of measurement sensitivity and
power. If the evidence still supports a null, make the rigorous null, audit tools,
and hard-task set the primary outputs. Do not present an underpowered experiment
as proof of no effect.

## Deployment sequence

1. **Local foundation:** run only the existing small scenarios and mock models until
   installation, scoring and analysis contracts are checked. No server is needed.
2. **GitHub source and CI:** choose the destination repo/visibility when publication
   is requested. Push a reviewed milestone, confirm hosted CI, then tag only the
   evidence actually completed. Verify ignored memory stays absent from tracked files.
3. **Pilot report:** generate a static page from a curated export with explicit pilot
   labels. Choose and verify GitHub Pages settings at that stage; record the deployed
   commit and URL. Local raw logs and unpublished results stay local.
4. **Full results:** build the site from versioned, reviewed public artifacts; keep
   credentials in the execution environment, not in the site. Show model/config IDs,
   sample counts, costs, uncertainty and exclusions alongside each result.
5. **Release:** pin the report to a source commit and data/config checksums. Roll back
   a faulty site by redeploying the previous reviewed artifact; preserve correction notes.

The dashboard is static. Model runs are batch jobs on the local machine or a
container host selected when the agentic stage needs one. Hosting/provider choices,
current model availability, and prices will be verified at their stage rather than
fixed speculatively now.

## Next session: stage 3 only

1. Read the local `MEMORY.md` and this plan; inspect Git status.
2. Review the draft local model configuration in `docs/pilot_config.md` and cost cap.
3. Add reviewed sycophancy pairs only after the owner supplies human scenario review.
4. Run a small real pilot with traceable run manifests and manual score spot-checks.

Model selection, paid runs, expanding scenarios, hard tasks, and deployment belong to
later stages. No production measurements or external publications have happened yet.

### Local provider note

The 2026-09-14 local inventory includes Ollama `qwen3.8:27b`, `gemma4:latest`,
`muse-glimmer:30b-mlx`, `qwen2.5:72b-instruct`, and an uncensored Qwen3.8 variant.
The first provider candidate is `ollama/qwen3.8:27b`; it is GPU-loaded and responds
through Inspect. Its hidden reasoning can consume a small completion cap, so stage 3
must choose and record an explicit reasoning/token policy. This connectivity check is
not a benchmark result. Hugging Face also has local Qwen 0.5B/1.5B/7B, Phi-3 Mini,
and Olmo-3 7B checkpoints, but no HF backend has been selected yet.
