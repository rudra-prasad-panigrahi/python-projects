from __future__ import annotations

import hashlib
import math
import re
from typing import Sequence


class EmbeddingService:
    """
    Embedding service with pure-Python fallback (hashed token vector with L2 normalization)
    and optional sentence-transformers integration.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dimension: int = 384,
    ) -> None:
        self.model_name = model_name
        self.dimension = dimension
        self._model = None

    def _hash_vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        for tok in tokens:
            # 1-gram hash
            h1 = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % self.dimension
            vec[h1] += 1.0
            # character 3-grams for fuzzy matching
            if len(tok) >= 3:
                for i in range(len(tok) - 2):
                    sub = tok[i : i + 3]
                    h2 = int(hashlib.sha256(sub.encode("utf-8")).hexdigest(), 16) % self.dimension
                    vec[h2] += 0.3

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            vec = [x / norm for x in vec]
        return vec

    def encode(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            if self._model is None:
                self._model = SentenceTransformer(self.model_name)
                try:
                    model_dim = int(self._model.get_sentence_embedding_dimension())
                    if model_dim > 0:
                        self.dimension = model_dim
                except Exception:
                    pass
            raw = self._model.encode(list(texts), normalize_embeddings=True)
            return [list(map(float, row)) for row in raw]
        except Exception:
            return [self._hash_vector(t) for t in texts]
