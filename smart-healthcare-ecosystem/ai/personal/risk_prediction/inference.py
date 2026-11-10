from __future__ import annotations

from .features import (
    RiskInput,
    to_feature_vector,
)
from .models.cardiovascular import (
    CardiovascularRiskModel,
)


class RiskPredictionService:
    def __init__(
        self,
        model: CardiovascularRiskModel | None = None,
    ) -> None:
        self.model = model or CardiovascularRiskModel()

    def predict(
        self,
        data: RiskInput,
    ) -> dict:
        vector = to_feature_vector(data)

        probability = self.model.predict_probability(vector)

        if probability < 0.20:
            category = "Low"
            interpretation = "Estimated statistical risk falls in the lower relative range based on submitted parameters."
        elif probability < 0.45:
            category = "Moderate"
            interpretation = "Estimated statistical risk falls in the moderate relative range based on submitted parameters."
        else:
            category = "Elevated"
            interpretation = "Estimated statistical risk falls in the higher relative range based on submitted parameters."

        return {
            "model_estimated_risk_category": category,
            "estimated_risk_probability": round(probability, 4),
            "risk_percentage": round(probability * 100.0, 1),
            "factors_evaluated": {
                "age": data.age,
                "bmi": data.bmi,
                "systolic_bp": data.systolic_bp,
                "glucose": data.glucose,
                "smoker": data.smoker,
                "family_history": data.family_history,
            },
            "model_type": "Tabular Cardiovascular Risk Prototype (Logistic Estimation)",
            "model_version": self.model.model_version,
            "status": "Prototype / Research Model",
            "interpretation": interpretation,
            "clinical_validity_note": (
                "PROTOTYPE / RESEARCH MODEL ONLY. This model estimate is strictly for decision-support "
                "and research exploration. It has not been approved as a diagnostic medical device by regulatory "
                "authorities and must not be used to confirm or rule out clinical cardiovascular disease."
            ),
            "disclaimer": "Informational research output only. Consult a licensed physician for clinical assessment.",
        }