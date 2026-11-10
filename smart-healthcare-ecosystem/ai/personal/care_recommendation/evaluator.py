from __future__ import annotations


def summary_completeness(
    summary: dict,
    expected_terms: set[str],
) -> float:
    if not expected_terms:
        return 1.0

    text = str(
        summary.get(
            "summary",
            "",
        )
    ).lower()

    found = sum(
        term.lower() in text
        for term in expected_terms
    )

    return found / len(expected_terms)