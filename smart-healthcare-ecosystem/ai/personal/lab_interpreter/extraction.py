from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LabValue:
    name: str
    value: float
    unit: str | None
    reference_min: float | None = None
    reference_max: float | None = None


PATTERNS = {
    "glucose": re.compile(
        r"(?:glucose|blood glucose)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(mg/dL)?",
        re.IGNORECASE,
    ),
    "hba1c": re.compile(
        r"(?:hba1c|a1c)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(%)?",
        re.IGNORECASE,
    ),
    "hemoglobin": re.compile(
        r"(?:hemoglobin|haemoglobin|hb)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(g/dL)?",
        re.IGNORECASE,
    ),
    "cholesterol": re.compile(
        r"(?:total cholesterol|cholesterol)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(mg/dL)?",
        re.IGNORECASE,
    ),
    "creatinine": re.compile(
        r"(?:creatinine)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(mg/dL)?",
        re.IGNORECASE,
    ),
}


def extract_lab_values(
    text: str,
) -> list[LabValue]:
    if not text.strip():
        return []

    results: list[LabValue] = []

    for name, pattern in PATTERNS.items():
        match = pattern.search(text)

        if not match:
            continue

        value = float(match.group(1))
        unit = match.group(2)

        results.append(
            LabValue(
                name=name,
                value=value,
                unit=unit,
            )
        )

    return results