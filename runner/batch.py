"""Execute bounded run manifests with resumable state and a cost cap.

This module deliberately treats Inspect as an external command. It does not parse
model output or turn failed runs into scores; :mod:`runner.export` remains the only
path into the validated result table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from runner.manifest import RunSpec

STATE_VERSION = 1
CommandExecutor = Callable[..., subprocess.CompletedProcess[str]]


def spec_key(spec: RunSpec) -> str:
    """Return a stable identifier for one exact manifest entry."""

    payload = json.dumps(spec.manifest_record(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _new_state(specs: list[RunSpec], budget_usd: float | None, cost_per_attempt_usd: float) -> dict[str, Any]:
    return {
        "version": STATE_VERSION,
        "budget_usd": budget_usd,
        "cost_per_attempt_usd": cost_per_attempt_usd,
        "spent_usd": 0.0,
        "runs": {
            spec_key(spec): {
                "spec": spec.manifest_record(),
                "status": "pending",
                "attempts": 0,
            }
            for spec in specs
        },
    }


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _load_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    state = json.loads(path.read_text())
    if not isinstance(state, dict) or state.get("version") != STATE_VERSION:
        raise ValueError(f"unsupported batch state at {path}")
    if not isinstance(state.get("runs"), dict):
        raise TypeError(f"batch state at {path} has no runs object")
    return state


class BatchRunner:
    """Run a manifest while preserving enough state to resume safely."""

    def __init__(
        self,
        specs: list[RunSpec],
        state_path: Path,
        *,
        retry_limit: int = 0,
        budget_usd: float | None = None,
        cost_per_attempt_usd: float = 0.0,
    ) -> None:
        if retry_limit < 0:
            raise ValueError("retry_limit must be non-negative")
        if budget_usd is not None and budget_usd < 0:
            raise ValueError("budget_usd must be non-negative")
        if cost_per_attempt_usd < 0:
            raise ValueError("cost_per_attempt_usd must be non-negative")
        keys = [spec_key(spec) for spec in specs]
        if len(keys) != len(set(keys)):
            raise ValueError("manifest contains duplicate run specifications")
        self.specs = specs
        self.state_path = state_path
        self.retry_limit = retry_limit
        self.budget_usd = budget_usd
        self.cost_per_attempt_usd = cost_per_attempt_usd

    def run(
        self,
        *,
        execute: CommandExecutor = subprocess.run,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Execute pending entries and return the persisted state.

        A successful entry is never rerun. Failed and timed-out entries are retried
        up to ``retry_limit`` additional attempts. State is written after every
        attempt, so an interrupted process can resume without duplicating completed
        entries.
        """

        state = _load_state(self.state_path)
        if state is None:
            state = _new_state(self.specs, self.budget_usd, self.cost_per_attempt_usd)
        self._check_compatible_state(state)
        if dry_run:
            for spec in self.specs:
                record = state["runs"][spec_key(spec)]
                if record["status"] == "pending":
                    record["status"] = "planned"
            _write_state(self.state_path, state)
            return state

        for spec in self.specs:
            key = spec_key(spec)
            record = state["runs"][key]
            if record["status"] == "success":
                continue
            if record["status"] == "planned":
                record["status"] = "pending"
            while record["attempts"] <= self.retry_limit:
                if not self._within_budget(state):
                    record["status"] = "blocked_budget"
                    _write_state(self.state_path, state)
                    break
                record["attempts"] += 1
                state["spent_usd"] = round(
                    float(state["spent_usd"]) + self.cost_per_attempt_usd, 8
                )
                started = time.monotonic()
                try:
                    completed = execute(
                        spec.command(),
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=spec.timeout,
                    )
                    record["returncode"] = completed.returncode
                    record["status"] = "success" if completed.returncode == 0 else "failed"
                    if completed.returncode != 0:
                        record["stderr_tail"] = (completed.stderr or "")[-1000:]
                except subprocess.TimeoutExpired as error:
                    record["status"] = "timeout"
                    record["error"] = str(error)
                except OSError as error:
                    record["status"] = "failed"
                    record["error"] = str(error)
                record["last_duration_seconds"] = round(time.monotonic() - started, 6)
                _write_state(self.state_path, state)
                if record["status"] == "success":
                    break
        _write_state(self.state_path, state)
        return state

    def _within_budget(self, state: dict[str, Any]) -> bool:
        budget = state.get("budget_usd")
        if budget is None:
            return True
        return float(state["spent_usd"]) + self.cost_per_attempt_usd <= float(budget) + 1e-9

    def _check_compatible_state(self, state: dict[str, Any]) -> None:
        expected = {spec_key(spec): spec.manifest_record() for spec in self.specs}
        actual = state["runs"]
        if set(actual) != set(expected):
            raise ValueError("manifest does not match the existing batch state")
        for key, spec in expected.items():
            if actual[key].get("spec") != spec:
                raise ValueError(f"manifest entry {key} differs from existing batch state")


def load_manifest(path: Path) -> list[RunSpec]:
    """Load the JSON list written by :func:`runner.manifest.write_manifest`."""

    records = json.loads(path.read_text())
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise ValueError("manifest must be a JSON list of objects")
    return [RunSpec(**record) for record in records]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state", type=Path, default=Path("logs/batch_state.json"))
    parser.add_argument("--retry-limit", type=int, default=0)
    parser.add_argument("--budget-usd", type=float)
    parser.add_argument("--cost-per-attempt-usd", type=float, default=0.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    runner = BatchRunner(
        load_manifest(args.manifest),
        args.state,
        retry_limit=args.retry_limit,
        budget_usd=args.budget_usd,
        cost_per_attempt_usd=args.cost_per_attempt_usd,
    )
    state = runner.run(dry_run=args.dry_run)
    counts: dict[str, int] = {}
    for record in state["runs"].values():
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(json.dumps({"runs": counts, "spent_usd": state["spent_usd"]}, sort_keys=True))


if __name__ == "__main__":
    main()
