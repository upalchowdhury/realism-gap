"""Deterministic scorer used only to verify offline Inspect plumbing.

The mock model emits a fixed sentence and cannot follow the honesty judge's
``GRADE: C``/``GRADE: I`` contract. This scorer therefore checks only that a
sample produced non-empty output. It is not a benchmark behavior label and is
never selected for a real-model run.
"""

from inspect_ai.scorer import Score, Scorer, Target, mean, scorer
from inspect_ai.solver import TaskState


@scorer(metrics=[mean()])
def offline_smoke() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        completion = state.output.completion or ""
        return Score(
            value=1.0 if completion.strip() else 0.0,
            answer="nonempty" if completion.strip() else "empty",
            explanation="offline plumbing check; not an honesty or misbehavior label",
        )

    return score
