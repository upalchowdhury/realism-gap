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
    model_base_url: str | None = None
    reasoning_effort: str | None = None

    def __post_init__(self) -> None:
        if self.realism not in {"lab", "wild"}:
            raise ValueError("realism must be 'lab' or 'wild'")
        if self.seed < 0 or self.paraphrase < 0:
            raise ValueError("seed and paraphrase must be non-negative")
        if self.max_tokens <= 0 or self.timeout <= 0 or self.max_connections <= 0:
            raise ValueError("resource bounds must be positive")
        if not self.model or not self.judge or not self.task_file:
            raise ValueError("task_file, model, and judge must be non-empty")
        if self.model_base_url is not None and not self.model_base_url.strip():
            raise ValueError("model_base_url must be non-empty when supplied")
        if self.reasoning_effort is not None and self.reasoning_effort not in {
            "none", "minimal", "low", "medium", "high", "xhigh", "max"
        }:
            raise ValueError("reasoning_effort is not a supported Inspect value")

    def command(self, inspect_executable: str = "inspect") -> list[str]:
        """Return the exact bounded Inspect command for this run."""

        command = [
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
        if self.model_base_url:
            command.extend(["--model-base-url", self.model_base_url])
        if self.reasoning_effort:
            command.extend(["--reasoning-effort", self.reasoning_effort])
        return command

    def manifest_record(self) -> dict[str, object]:
        """Return a JSON-serializable record suitable for a run manifest."""

        return asdict(self)


def write_manifest(path: Path, specs: list[RunSpec]) -> None:
    """Write a deterministic JSON manifest without execution side effects."""

    import json

    records = [spec.manifest_record() for spec in specs]
    path.write_text(json.dumps(records, indent=2) + "\n")
