from __future__ import annotations

from typing import Any

from .features import build_adherence_features
from .model import MedicationAdherenceModel


def predict_adherence(
    events: list[dict[str, Any]],
    model: MedicationAdherenceModel | None = None,
) -> dict[str, Any]:
    features = build_adherence_features(events)

    scheduled = int(features["doses_scheduled"])
    taken = int(features["doses_taken"])
    missed = int(features["missed_doses"])
    late = int(features["late_doses"])

    observed_rate = (taken / scheduled) if scheduled > 0 else 1.0

    if model is None:
        model = MedicationAdherenceModel()

    try:
        model_probability = model.predict_probability(features)
    except Exception:
        model_probability = observed_rate

    adherence_percentage = round(observed_rate * 100.0, 1)

    if adherence_percentage >= 85:
        category = "High Adherence"
    elif adherence_percentage >= 65:
        category = "Moderate Adherence"
    else:
        category = "Needs Attention"

    return {
        "observed_adherence_rate": round(observed_rate, 4),
        "adherence_percentage": adherence_percentage,
        "predicted_adherence_probability": round(model_probability, 4),
        "adherence_category": category,
        "doses_scheduled": scheduled,
        "doses_taken": taken,
        "missed_doses": missed,
        "late_doses": late,
        "days_since_last_missed": features["days_since_last_missed"],
        "days_in_period": features["days_in_period"],
        "model_type": "Logistic Regression Adherence Estimator",
        "model_version": model.model_version,
        "informational_note": (
            "Medication adherence predictions are informational and provide decision support. "
            "Schedules and dosages are never modified automatically."
        ),
    }