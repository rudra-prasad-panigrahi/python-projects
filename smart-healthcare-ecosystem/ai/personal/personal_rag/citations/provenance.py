from __future__ import annotations

from typing import Any


def build_citations(
    retrieved_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []

    seen: set[tuple[str, str]] = set()

    for index, item in enumerate(
        retrieved_items,
        start=1,
    ):
        metadata = item.get(
            "metadata",
            {},
        )

        document_id = str(
            metadata.get(
                "document_id",
                "",
            )
        )

        record_id = str(
            metadata.get(
                "record_id",
                "",
            )
        )

        identity = (
            document_id,
            record_id,
        )

        if identity in seen:
            continue

        seen.add(identity)

        citations.append(
            {
                "citation_id": f"S{index}",
                "document_id": (
                    document_id
                    or None
                ),
                "record_id": (
                    record_id
                    or None
                ),
                "filename": metadata.get(
                    "filename"
                ),
                "source": metadata.get(
                    "source"
                ),
                "date": metadata.get(
                    "date"
                ),
                "score": item.get(
                    "score"
                ),
            }
        )

    return citations