from __future__ import annotations

from typing import Any

from .extraction import LabValue


def interpret_lab_result(
    result: LabValue,
) -> dict[str, Any]:
    status = "unknown"

    if (
        result.reference_min is not None
        and result.reference_max is not None
    ):
        if result.value < result.reference_min:
            status = "below_reference"

        elif result.value > result.reference_max:
            status = "above_reference"

        else:
            status = "within_reference"

    return {
        "name": result.name,
        "value": result.value,
        "unit": result.unit,
        "status": status,
        "reference_min": result.reference_min,
        "reference_max": result.reference_max,
        "explanation": build_explanation(
            result,
            status,
        ),
    }


def build_explanation(
    result: LabValue,
    status: str,
) -> str:
    if status == "within_reference":
        return (
            f"{result.name} is within the supplied "
            "reference range."
        )

    if status == "above_reference":
        return (
            f"{result.name} is above the supplied "
            "reference range."
        )

    if status == "below_reference":
        return (
            f"{result.name} is below the supplied "
            "reference range."
        )

    return (
        f"{result.name} was extracted from the supplied "
        "data, but no reference range was provided."
    )


def interpret_lab_results(
    results: list[LabValue],
) -> list[dict[str, Any]]:
    return [
        interpret_lab_result(result)
        for result in results
    ]