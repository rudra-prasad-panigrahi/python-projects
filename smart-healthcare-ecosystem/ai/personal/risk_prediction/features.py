from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskInput:
    age: float
    bmi: float
    systolic_bp: float
    glucose: float
    smoker: bool
    family_history: bool


def to_feature_vector(
    data: RiskInput,
) -> list[float]:
    return [
        float(data.age),
        float(data.bmi),
        float(data.systolic_bp),
        float(data.glucose),
        float(data.smoker),
        float(data.family_history),
    ]