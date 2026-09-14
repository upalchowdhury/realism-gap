# The Realism Gap Sprint — flagship project plan (decided 2026-09-13, amended same day with METR track + public-trail plan)

User profile: AI engineer/architect, 8-week full-time sprint (Sep 14 – Nov 8, 2026), wants to be well-rounded, goal is job at evals org OR company — keep both open.

Full plan artifact: https://claude.ai/code/artifact/a375ce47-4fe6-4faa-bb97-3df113b6129a
Repo skeleton delivered 2026-09-13 as realism-gap-skeleton.zip (Inspect task w/ lab+wild pair, awareness probe scorer, honesty rubric, scenario validator with eval-tells regex, paired-bootstrap gap.py + tests, CI, hard-task template with QA log + baseline sheet, decision record 0001, AI_USE.md, week-01 log template). Note: inspect-ai could not be installed in the sandbox (PyPI 403 via proxy), so the Inspect task code was written against the known API but not executed; user must run `inspect eval tasks/sycophancy_feedback/task.py --model mockllm/model --limit 2` on day one and fix any API drift.

## What to build
A paired-realism behavioral eval benchmark on Inspect (UK AISI). For each behavior family, every scenario exists as a matched pair: a "lab" version (obvious eval) and a "wild" version (realistic context, tools, history, stakes, no eval tells). Headline metric per behavior and model:

gap_b = P(misbehave | wild_b) − P(misbehave | lab_b), 95% CI via paired bootstrap over scenarios × seeds × paraphrases, plus an awareness probe (does the model flag/reason that it's being tested).

Why: evaluation awareness/sandbagging is the central open problem in evals in 2026 (Opus 4.6 system card: ~80% eval recognition, ~2% verbalized); no open reproducible benchmark quantifies the lab→deployment transfer gap.

## Components
A. Environments — 4 families: sycophancy (feedback + factual capitulation), user-directed deception, sandbagging, reward hacking in agentic coding. ~20 scenarios each × 2 realism × 3 paraphrases. Agentic ones in Inspect Docker sandbox. Every scenario carries pair_id.
B. Harness & rigor — Inspect tasks, rule-based + model-graded scorers, 120 hand-labeled transcripts for judge validation (target κ ≥ 0.75), 8 models × 5 seeds, cached resumable distributed runner with cost ledger (< $400 full run).
C. Reporting & audit — public dashboard, methodology doc mapped to AEF-one minimum operating conditions, "eval-tells" realism checklist applied to 3 existing public evals, paper-style write-up, PR to inspect_evals.
D. METR track (added after checking the METR Task Development Engineer contractor posting) — 4–6 hard, self-contained, long-horizon software/ML tasks (2–8 h human time) in METR's task standard with hidden test-based scorers: multi-service refactor vs failing integration suite; data-pipeline migration with hidden schema drift; ML training-loop bug hunt to a target metric; reverse-engineer an undocumented API. Each has a spec, a task-spec QA checklist + ambiguity log, the user's own timed solve as a human baseline (one outside baseliner for two tasks). Run them through METR's open-source Hawk. These tasks are the capability substrate for the sandbagging family and their editable test suites feed the reward-hacking family. Week 6: plot model success vs human baseline time (mini Time Horizons curve).

Coverage of the METR posting: original plan ~60% (Inspect, sandboxing, rigor, SWE); with track D ~90% (everything but prior in-house Hawk use).

## Weeks
1. Foundations: read HELM, ELEPHANT, AI Sandbagging, Alignment Faking, Apollo in-context scheming, "In-Context Environments Induce Evaluation-Awareness", METR Time Horizons methodology; Inspect docs; reproduce one inspect_evals task on 3 models; public reproduction log; repo + CI.
2. Design doc (taxonomy, threat models, metric, scenario spec, eval-tells checklist, judge rubric, model list, hard-task specs); build sycophancy pair ×10, pilot on 2 models; get 3 expert critiques.
3–4. Build all 4 behavior families + the 4 hard tasks (solve each yourself, timed); scenario pipeline (LLM-drafted, human-edited); sandbox; hand-label 120; start anomalies log. Open inspect_evals PR as DRAFT in week 4.
5. Run at scale; build runner (cache, retries, resume, cost ledger); also run hard tasks on Hawk; dashboard public + pinned; root-cause anomalies. APPLY TO METR CONTRACTOR ROLE THIS WEEK with 2–3 finished tasks (contract role, lower bar, would fund weeks 6–8).
6. Analysis: paired bootstrap gaps, awareness–gap correlation, paraphrase/seed robustness; mini time-horizon curve; 3 realism audits; report nulls prominently.
7. Write-up (arXiv + AF/LW), inspect_evals PR to ready, 5-min demo video, AEF-one methodology doc.
8. Apply (Anthropic, Apollo, AISI, Epoch, FAR); 5 discovery calls with third-party evaluators/audit orgs (Fathom, AEF, Guidelight) on "would you pay for a recurring realism audit"; decision memo: job track vs company track.

Kill criterion (end of wk 4): if gaps ≈ 0 everywhere and awareness probe never fires, reframe as rigorous null + make the audit checklist/tooling and the hard-task set the primary artifacts.

## Working in public
Rule: every post links to a commit, a transcript, or a number.
- GitHub: one repo `realism-gap` (README = results page; tasks/<family>/lab.jsonl + wild.jsonl side by side; hard_tasks/; docs/decisions/ with rejected alternatives; docs/log/ weekly "built / surprised me / unsure about"; dashboard on GitHub Pages; release tags v0.1-reproduction, v0.2-design, v0.3-pilot, v1.0-results; CI green).
- Long-form (LW/AF + own blog): wk1 reproduction log, wk2 design doc asking for critique, wk7 report.
- Weekly Friday thread on X, mirrored to LinkedIn: one artifact per thread (a pair, a weird transcript, a gap with CI, judge κ, cost ledger). Lead with the finding.
- 10 min/day replies to AISI/Apollo/METR/Epoch posts with something specific from own data.
- Avoid: "day N of learning AI safety" with no artifact, paper restating, emoji threads, frontier-model claims without n/seeds/link.

## Proving the work is yours (AI coding tools assumed)
Judgment leaves fingerprints models can't fake: docs/decisions/ with rejected alternatives; 120 hand labels with disagreements vs judge; anomaly log with root causes; timed human baselines; paraphrase 0 of every pair hand-written; docs/AI_USE.md disclosure; inspect_evals PR review thread; self-review comments on AI-written code in PRs; 5-min demo video explaining decisions.

## Alternatives set aside
- Eval Doctor (benchmark contamination/noise/power auditor): great infra signal, weak alignment tie; rigor slice folded into B.
- Domain agentic benchmark (GDPval/SWE-Lancer style): crowded, expensive to grade, weak alignment tie; partially absorbed by track D.

## Rhythm
60% build / 20% read / 20% write in public. Post weekly. Never use LLMs for the 120 hand labels or the timed baselines.