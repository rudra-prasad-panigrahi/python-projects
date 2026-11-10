from __future__ import annotations


def retrieval_recall_at_k(
    retrieved_document_ids: list[str],
    relevant_document_ids: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    if not relevant_document_ids:
        return 0.0

    retrieved = set(
        retrieved_document_ids[:k]
    )

    hits = len(
        retrieved.intersection(
            relevant_document_ids
        )
    )

    return hits / len(
        relevant_document_ids
    )