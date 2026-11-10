"""Bounded, traceable text chunking for document retrieval."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    text: str
    index: int
    document_id: str

def chunk_text(text: str, document_id: str, max_chars: int = 1200, overlap: int = 120) -> list[Chunk]:
    if max_chars <= overlap: raise ValueError("max_chars must be greater than overlap")
    clean = " ".join(text.split())
    if not clean: return []
    step = max_chars - overlap
    return [Chunk(clean[start:start + max_chars], index, document_id) for index, start in enumerate(range(0, len(clean), step))]
