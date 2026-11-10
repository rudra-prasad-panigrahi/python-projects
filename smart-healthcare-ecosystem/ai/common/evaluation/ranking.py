from __future__ import annotations

from collections.abc import Iterable


def precision_at_k(
    predicted_ids: Iterable[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    predicted = list(predicted_ids)[:k]

    if not predicted:
        return 0.0

    hits = sum(
        item in relevant_ids
        for item in predicted
    )

    return hits / len(predicted)


def recall_at_k(
    predicted_ids: Iterable[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    if not relevant_ids:
        return 0.0

    predicted = set(
        list(predicted_ids)[:k]
    )

    hits = len(
        predicted.intersection(
            relevant_ids
        )
    )

    return hits / len(relevant_ids)