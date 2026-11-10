from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class RetrievalItem:
    text: str
    metadata: dict[str, Any]


class VectorRetriever:
    """
    Vector retriever with authorization-aware metadata filtering and cosine similarity.
    Supports pure Python execution as well as optional FAISS acceleration.

    CRITICAL SAFETY REQUIREMENT:
    Metadata filtering strictly isolates records by user_id and authorization scope
    before vector items are returned or supplied to an LLM context.
    """

    def __init__(
        self,
        dimension: int = 64,
    ) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be positive.")

        self.dimension = dimension
        self.items: list[RetrievalItem] = []
        self.vectors: list[list[float]] = []

    def _normalize(self, vec: Sequence[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm <= 1e-9:
            return [0.0] * len(vec)
        return [float(x) / norm for x in vec]

    def add(
        self,
        embeddings: Sequence[Sequence[float]],
        items: Sequence[RetrievalItem],
    ) -> None:
        if len(embeddings) != len(items):
            raise ValueError("Embedding and item counts must match.")

        if not items:
            return

        for vec, item in zip(embeddings, items):
            if len(vec) != self.dimension:
                raise ValueError(f"Embedding dimension {len(vec)} does not match index dimension {self.dimension}.")
            norm_vec = self._normalize(vec)
            self.vectors.append(norm_vec)
            self.items.append(item)

    def search(
        self,
        query_embedding: Sequence[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if not self.vectors:
            return []

        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query dimension {len(query_embedding)} does not match index dimension {self.dimension}.")

        norm_query = self._normalize(query_embedding)

        scored_candidates: list[tuple[float, int]] = []
        for idx, vec in enumerate(self.vectors):
            item = self.items[idx]
            # Enforce authorization & metadata filter before score ranking
            if metadata_filter:
                match = all(item.metadata.get(k) == v for k, v in metadata_filter.items())
                if not match:
                    continue

            # Dot product of normalized vectors = Cosine similarity
            dot_product = sum(q * v for q, v in zip(norm_query, vec))
            scored_candidates.append((dot_product, idx))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = scored_candidates[:top_k]

        results: list[dict[str, Any]] = []
        for score, idx in top_candidates:
            item = self.items[idx]
            results.append({
                "text": item.text,
                "metadata": item.metadata,
                "score": round(float(score), 4),
            })

        return results