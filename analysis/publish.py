"""Build a validated aggregate gap table and static dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from analysis.dashboard import write_dashboard
from analysis.gap import gap_table


def publish(
    results_path: Path,
    table_path: Path,
    dashboard_path: Path,
    *,
    n_boot: int = 10_000,
    seed: int = 0,
) -> pd.DataFrame:
    """Aggregate validated result rows and write the CSV plus dashboard.

    ``analysis.gap`` validates the complete paired identity contract before any
    estimate is calculated. Invalid or incomplete inputs fail without writing an
    aggregate table or dashboard.
    """

    if n_boot <= 0:
        raise ValueError("n_boot must be positive")
    if seed < 0:
        raise ValueError("seed must be non-negative")
    results = pd.read_csv(results_path)
    aggregate = gap_table(results, n_boot=n_boot, seed=seed)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    aggregate.to_csv(table_path, index=False)
    write_dashboard(table_path, dashboard_path)
    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="validated long-format result CSV")
    parser.add_argument("table", type=Path, help="output aggregate gap CSV")
    parser.add_argument("dashboard", type=Path, help="output static dashboard HTML")
    parser.add_argument("--bootstrap", type=int, default=10_000, dest="n_boot")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    aggregate = publish(
        args.results,
        args.table,
        args.dashboard,
        n_boot=args.n_boot,
        seed=args.seed,
    )
    print(f"Wrote {args.table} and {args.dashboard} ({len(aggregate)} estimates)")


if __name__ == "__main__":
    main()
