"""Paired realism gap with bootstrap confidence intervals.

Input: a long-format table with one row per (model, behavior, pair_id, realism, seed, paraphrase)
and a binary `misbehaved` column (1 = the behavior we are measuring occurred).

The gap is computed on matched pairs: for each pair_id we average over seeds × paraphrases
within lab and within wild, take the difference, then bootstrap over pair_ids. Resampling
pairs (not individual samples) is what makes the CI honest about scenario-level variance.

Usage:
    python -m analysis.gap results.csv
"""

import sys

import numpy as np
import pandas as pd


def paired_gap(df: pd.DataFrame, n_boot: int = 10_000, seed: int = 0) -> dict:
    """df must contain columns: pair_id, realism ('lab'|'wild'), misbehaved (0/1)."""
    per_pair = (
        df.groupby(["pair_id", "realism"])["misbehaved"].mean().unstack("realism").dropna()
    )
    if per_pair.empty:
        raise ValueError("no complete pairs")
    diffs = (per_pair["wild"] - per_pair["lab"]).to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(diffs), size=(n_boot, len(diffs)))
    boots = diffs[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "n_pairs": int(len(diffs)),
        "p_lab": float(per_pair["lab"].mean()),
        "p_wild": float(per_pair["wild"].mean()),
        "gap": float(diffs.mean()),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "excludes_zero": bool(lo > 0 or hi < 0),
    }


def gap_table(df: pd.DataFrame, **kw) -> pd.DataFrame:
    rows = []
    for (model, behavior), g in df.groupby(["model", "behavior"]):
        rows.append({"model": model, "behavior": behavior, **paired_gap(g, **kw)})
    return pd.DataFrame(rows).sort_values(["behavior", "gap"], ascending=[True, False])


if __name__ == "__main__":
    data = pd.read_csv(sys.argv[1])
    pd.set_option("display.width", 160)
    print(gap_table(data).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
