import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.gap import paired_gap
from analysis.results import grade_to_misbehaved, score_records, validate_results
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
