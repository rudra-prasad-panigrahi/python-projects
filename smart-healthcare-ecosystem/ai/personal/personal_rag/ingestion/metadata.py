from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path


def calculate_sha256(
    data: bytes,
) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def build_document_metadata(
    *,
    user_id: str,
    document_id: str,
    filename: str,
    data: bytes,
    source: str = "user_upload",
) -> dict:
    path = Path(filename)

    return {
        "user_id": user_id,
        "document_id": document_id,
        "filename": path.name,
        "extension": path.suffix.lower(),
        "source": source,
        "sha256": calculate_sha256(data),
        "ingested_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }