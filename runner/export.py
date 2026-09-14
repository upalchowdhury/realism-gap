"""Convert Inspect JSON log dumps into validated analysis result rows."""

from collections.abc import Iterable, Mapping

import pandas as pd

from analysis.results import score_records


def records_from_logs(
    logs: Iterable[Mapping[str, object]],
    *,
    default_seed: int = 0,
    scorer_name: str = "model_graded_qa",
) -> pd.DataFrame:
    """Extract exact rubric grades from one or more Inspect log dictionaries.

    Logs must include the model, behavior/realism metadata, and each sample's
    pair/paraphrase metadata. A log's ``task_args.seed`` overrides ``default_seed``.
    The resulting combined table is passed through ``score_records`` so both
    realism sides and every repetition identity are checked before returning.
    """

    records: list[dict[str, object]] = []
    for log_index, log in enumerate(logs):
        evaluation = _mapping(log, "eval", log_index)
        model = _required(evaluation, "model", f"log {log_index}")
        task_args = evaluation.get("task_args", {})
        if not isinstance(task_args, Mapping):
            raise TypeError(f"log {log_index} task_args must be an object")
        seed = task_args.get("seed", default_seed)
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError(f"log {log_index} seed must be a non-negative integer")

        samples = log.get("samples")
        if not isinstance(samples, list) or not samples:
            raise ValueError(f"log {log_index} samples must be a non-empty list")
        for sample_index, sample in enumerate(samples):
            if not isinstance(sample, Mapping):
                raise TypeError(f"log {log_index} sample {sample_index} must be an object")
            metadata = sample.get("metadata")
            if not isinstance(metadata, Mapping):
                raise TypeError(f"log {log_index} sample {sample_index} metadata is required")
            fields = {
                field: _required(metadata, field, f"log {log_index} sample {sample_index}")
                for field in ("behavior", "pair_id", "realism", "paraphrase")
            }
            scores = sample.get("scores")
            if not isinstance(scores, Mapping) or scorer_name not in scores:
                raise ValueError(
                    f"log {log_index} sample {sample_index} is missing scorer {scorer_name!r}"
                )
            score = scores[scorer_name]
            if not isinstance(score, Mapping):
                raise TypeError(f"log {log_index} sample {sample_index} score must be an object")
            grade = score.get("value")
            if not isinstance(grade, str) or grade not in {"C", "I"}:
                raise ValueError(
                    f"log {log_index} sample {sample_index} has invalid or unscored grade {grade!r}"
                )
            records.append({"model": model, "seed": seed, **fields, "grade": grade})

    return score_records(records)


def _mapping(value: Mapping[str, object], key: str, context: int) -> Mapping[str, object]:
    nested = value.get(key)
    if not isinstance(nested, Mapping):
        raise TypeError(f"log {context} is missing object {key!r}")
    return nested


def _required(mapping: Mapping[str, object], key: str, context: str) -> object:
    value = mapping.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{context} is missing {key!r}")
    return value
