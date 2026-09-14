"""Run specifications for bounded, reproducible pilot executions."""

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunSpec:
    """One task/realism/model execution and its resource bounds."""

    task_file: str
    model: str
    judge: str
    realism: str
    seed: int
    paraphrase: int
    max_tokens: int = 1024
    timeout: int = 120
    max_connections: int = 1

    def __post_init__(self) -> None:
        if self.realism not in {"lab", "wild"}:
            raise ValueError("realism must be 'lab' or 'wild'")
        if self.seed < 0 or self.paraphrase < 0:
            raise ValueError("seed and paraphrase must be non-negative")
        if self.max_tokens <= 0 or self.timeout <= 0 or self.max_connections <= 0:
            raise ValueError("resource bounds must be positive")
        if not self.model or not self.judge or not self.task_file:
            raise ValueError("task_file, model, and judge must be non-empty")

    def command(self, inspect_executable: str = "inspect") -> list[str]:
        """Return the exact bounded Inspect command for this run."""

        return [
            inspect_executable,
            "eval",
            self.task_file,
            "-T",
            f"realism={self.realism}",
            "-T",
            f"judge={self.judge}",
            "--model",
            self.model,
            "--max-tokens",
            str(self.max_tokens),
            "--max-connections",
            str(self.max_connections),
            "--timeout",
            str(self.timeout),
        ]

    def manifest_record(self) -> dict[str, object]:
        """Return a JSON-serializable record suitable for a run manifest."""

        return asdict(self)


def write_manifest(path: Path, specs: list[RunSpec]) -> None:
    """Write a deterministic JSON manifest without execution side effects."""

    import json

    records = [spec.manifest_record() for spec in specs]
    path.write_text(json.dumps(records, indent=2) + "\n")
