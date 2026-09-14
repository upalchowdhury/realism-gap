from pathlib import Path

import numpy as np
import pandas as pd

from analysis.gap import paired_gap
from runner.validate import validate

ROOT = Path(__file__).resolve().parents[1]


def _synthetic(p_lab: float, p_wild: float, n_pairs: int = 60, reps: int = 15, seed: int = 1):
    rng = np.random.default_rng(seed)
    rows = []
    for pid in range(n_pairs):
        for realism, p in (("lab", p_lab), ("wild", p_wild)):
            for r in range(reps):
                rows.append({"pair_id": f"p{pid}", "realism": realism,
                             "misbehaved": int(rng.random() < p), "rep": r})
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
