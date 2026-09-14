import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.dashboard import render_dashboard, write_dashboard
from analysis.gap import paired_gap
from analysis.results import grade_to_misbehaved, score_records, validate_results
from runner.batch import BatchRunner, load_manifest, spec_key
from runner.export import records_from_logs
from runner.manifest import RunSpec, write_manifest
from runner.validate import validate

ROOT = Path(__file__).resolve().parents[1]


def _synthetic(p_lab: float, p_wild: float, n_pairs: int = 60, reps: int = 15, seed: int = 1):
    rng = np.random.default_rng(seed)
    rows = []
    for pid in range(n_pairs):
        for realism, p in (("lab", p_lab), ("wild", p_wild)):
            for r in range(reps):
                rows.append({"pair_id": f"p{pid}", "realism": realism,
                             "model": "synthetic", "behavior": "test_behavior",
                             "seed": 0, "paraphrase": r,
                             "misbehaved": int(rng.random() < p)})
    return pd.DataFrame(rows)


def test_gap_recovers_true_difference():
    res = paired_gap(_synthetic(0.20, 0.50), n_boot=2000)
    assert abs(res["gap"] - 0.30) < 0.08
    assert res["ci_lo"] > 0 and res["excludes_zero"]


def test_null_gap_ci_covers_zero():
    res = paired_gap(_synthetic(0.35, 0.35), n_boot=2000)
    assert res["ci_lo"] <= 0 <= res["ci_hi"]
    assert not res["excludes_zero"]


def test_bundled_scenarios_validate():
    assert validate(ROOT / "tasks") == []


def test_honesty_grade_conversion_is_explicit():
    assert grade_to_misbehaved(" C ") == 0
    assert grade_to_misbehaved("i") == 1
    for invalid in (None, "", "A", "GRADE: C"):
        try:
            grade_to_misbehaved(invalid)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"expected invalid grade to fail: {invalid!r}")


def test_score_fixture_converts_and_reaches_expected_gap():
    fixture = pd.read_csv(ROOT / "tests/fixtures/scores.csv")
    results = score_records(fixture.to_dict("records"))
    assert set(results["misbehaved"]) == {0, 1}
    result = paired_gap(results, n_boot=1000)
    assert result["n_pairs"] == 2
    assert result["p_lab"] == 0.5
    assert result["p_wild"] == 1.0
    assert result["gap"] == 0.5


def test_result_validation_rejects_unmatched_or_duplicate_identity():
    valid = pd.DataFrame(
        [
            {"model": "m", "behavior": "b", "pair_id": "p", "realism": "lab",
             "seed": 0, "paraphrase": 0, "misbehaved": 0},
            {"model": "m", "behavior": "b", "pair_id": "p", "realism": "wild",
             "seed": 0, "paraphrase": 0, "misbehaved": 1},
        ]
    )
    validate_results(valid)
    with_duplicate = pd.concat([valid, valid.iloc[[0]]], ignore_index=True)
    try:
        validate_results(with_duplicate)
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate result identity was accepted")

    unmatched = valid.iloc[[0]].copy()
    try:
        paired_gap(unmatched)
    except ValueError as error:
        assert "unmatched" in str(error)
    else:
        raise AssertionError("unmatched result identity was accepted")


def test_scenario_validator_rejects_duplicate_and_mismatched_paraphrase(tmp_path):
    family = tmp_path / "family"
    family.mkdir()
    row = {"id": "p_lab_0", "pair_id": "p", "behavior": "b", "realism": "lab",
           "paraphrase": 0, "input": "request", "target": "criterion"}
    (family / "lab.jsonl").write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n")
    wild = dict(row, id="p_wild_1", realism="wild", paraphrase=1)
    (family / "wild.jsonl").write_text(json.dumps(wild) + "\n")
    errors = validate(tmp_path)
    assert any("duplicate id" in error for error in errors)
    assert any("mismatched paraphrases" in error for error in errors)


def test_run_spec_is_explicit_and_bounded(tmp_path):
    spec = RunSpec(
        task_file="tasks/sycophancy_feedback/task.py",
        model="ollama/qwen3.8:27b",
        judge="ollama/gemma4:latest",
        realism="wild",
        seed=2,
        paraphrase=1,
        max_tokens=1024,
        timeout=120,
    )
    assert spec.command("inspect") == [
        "inspect", "eval", "tasks/sycophancy_feedback/task.py", "-T", "realism=wild",
        "-T", "judge=ollama/gemma4:latest", "--model", "ollama/qwen3.8:27b",
        "--max-tokens", "1024", "--max-connections", "1", "--timeout", "120",
    ]
    manifest = tmp_path / "manifest.json"
    write_manifest(manifest, [spec])
    assert json.loads(manifest.read_text()) == [spec.manifest_record()]


def test_run_spec_rejects_unbounded_or_invalid_values():
    common = {"task_file": "task.py", "model": "m", "judge": "j", "realism": "lab",
              "seed": 0, "paraphrase": 0}
    for field, value in (("realism", "other"), ("max_tokens", 0), ("timeout", 0), ("seed", -1)):
        try:
            RunSpec(**{**common, field: value})
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid RunSpec value accepted: {field}={value!r}")


def _run_spec():
    return RunSpec(
        task_file="tasks/sycophancy_feedback/task.py",
        model="mockllm/model",
        judge="mockllm/model",
        realism="lab",
        seed=0,
        paraphrase=0,
    )


def test_batch_runner_retries_and_resumes_success(tmp_path):
    spec = _run_spec()
    state_path = tmp_path / "state.json"
    calls = []

    def flaky(command, **kwargs):
        calls.append((command, kwargs))
        code = 1 if len(calls) == 1 else 0
        return subprocess.CompletedProcess(command, code, "", "temporary failure" if code else "")

    state = BatchRunner(specs=[spec], state_path=state_path, retry_limit=1).run(execute=flaky)
    record = state["runs"][spec_key(spec)]
    assert record["status"] == "success"
    assert record["attempts"] == 2
    assert len(calls) == 2

    resumed = BatchRunner(specs=[spec], state_path=state_path, retry_limit=1).run(execute=flaky)
    assert resumed["runs"][spec_key(spec)]["attempts"] == 2
    assert len(calls) == 2


def test_batch_runner_enforces_budget_and_dry_run(tmp_path):
    spec = _run_spec()
    state_path = tmp_path / "state.json"
    planned = BatchRunner(
        specs=[spec], state_path=state_path, budget_usd=0.05, cost_per_attempt_usd=0.05
    ).run(dry_run=True)
    assert planned["runs"][spec_key(spec)]["status"] == "planned"

    def succeeds(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, "", "")

    blocked = BatchRunner(
        specs=[spec], state_path=state_path, budget_usd=0.05, cost_per_attempt_usd=0.05
    ).run(execute=succeeds)
    assert blocked["runs"][spec_key(spec)]["status"] == "success"
    assert blocked["spent_usd"] == 0.05

    second_spec = RunSpec(**{**spec.manifest_record(), "paraphrase": 1})
    two_state = tmp_path / "two.json"
    limited = BatchRunner(
        specs=[spec, second_spec], state_path=two_state, budget_usd=0.05,
        cost_per_attempt_usd=0.05,
    ).run(execute=succeeds)
    statuses = {record["status"] for record in limited["runs"].values()}
    assert statuses == {"success", "blocked_budget"}


def test_checked_in_offline_manifest_loads():
    specs = load_manifest(ROOT / "examples/offline_manifest.json")
    assert [spec.realism for spec in specs] == ["lab", "wild"]
    assert all(spec.model == "mockllm/model" for spec in specs)


def _inspect_log(realism, grades, seed=3):
    samples = []
    for pair_id, grade in grades.items():
        samples.append(
            {
                "metadata": {
                    "pair_id": pair_id,
                    "behavior": "sycophancy_feedback",
                    "realism": realism,
                    "paraphrase": 0,
                },
                "scores": {"model_graded_qa": {"value": grade}},
            }
        )
    return {
        "eval": {"model": "fixture-model", "task_args": {"seed": seed}},
        "samples": samples,
    }


def test_inspect_logs_export_to_validated_results():
    logs = [
        _inspect_log("lab", {"p1": "C", "p2": "I"}),
        _inspect_log("wild", {"p1": "I", "p2": "I"}),
    ]
    results = records_from_logs(logs)
    assert len(results) == 4
    assert set(results["misbehaved"]) == {0, 1}
    assert paired_gap(results, n_boot=1000)["gap"] == 0.5


def test_inspect_log_export_rejects_unscored_grade():
    log = _inspect_log("lab", {"p1": None})
    try:
        records_from_logs([log])
    except ValueError as error:
        assert "invalid or unscored" in str(error)
    else:
        raise AssertionError("unscored Inspect sample was accepted")


def test_dashboard_empty_state_has_no_fake_results():
    page = render_dashboard()
    assert "No published results yet" in page
    assert "0.500" not in page
    assert "benchmark measurements" in page


def test_dashboard_renders_gap_bars_and_intervals():
    table = pd.DataFrame(
        [{"model": "fixture", "behavior": "sycophancy_feedback", "gap": 0.5,
          "ci_lo": 0.1, "ci_hi": 0.8, "n_pairs": 2}]
    )
    page = render_dashboard(table)
    assert "fixture" in page
    assert "+0.500" in page
    assert "[+0.100, +0.800]" in page
    assert "class=\"bar positive\"" in page


def test_dashboard_writer_reads_aggregate_csv(tmp_path):
    source = tmp_path / "gap_table.csv"
    destination = tmp_path / "site" / "index.html"
    pd.DataFrame(
        [{"model": "fixture", "behavior": "b", "gap": -0.25,
          "ci_lo": -0.5, "ci_hi": 0.1, "n_pairs": 4}]
    ).to_csv(source, index=False)
    write_dashboard(source, destination)
    page = destination.read_text()
    assert "fixture" in page
    assert "-0.250" in page
