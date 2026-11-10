from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class MedicationAdherenceModel:
    model_version: str = "1.0.0-adherence-model"
    # Coefficients for: [days_in_period, doses_scheduled, doses_taken, missed_doses, late_doses, days_since_last_missed]
    intercept: float = 0.85
    weights: tuple[float, float, float, float, float, float] = (
        0.01,   # days in period
        -0.05,  # scheduled
        0.18,   # taken
        -0.45,  # missed
        -0.20,  # late
        0.08,   # days since last missed
    )

    def predict_probability(self, features: dict[str, Any]) -> float:
        vector = [
            float(features.get("days_in_period", 0)),
            float(features.get("doses_scheduled", 0)),
            float(features.get("doses_taken", 0)),
            float(features.get("missed_doses", 0)),
            float(features.get("late_doses", 0)),
            float(features.get("days_since_last_missed", 0)),
        ]
        
        linear_val = self.intercept
        for w, x in zip(self.weights, vector):
            linear_val += w * x

        linear_val = max(-20.0, min(20.0, linear_val))
        prob = 1.0 / (1.0 + math.exp(-linear_val))
        return prob