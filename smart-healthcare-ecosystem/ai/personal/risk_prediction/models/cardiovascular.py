"""Cardiovascular risk prediction research prototype.

This module provides an isolated, non-clinical research prototype model for decision support.
It is explicitly labeled as a research model and does not provide clinical diagnoses.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CardiovascularRiskModel:
    model_version: str = "1.0.0-research-prototype"
    dataset_version: str = "synthetic-cvd-v1"
    
    # Feature weights (Age, BMI, Systolic BP, Glucose, Smoker, Family History)
    # Calibrated baseline intercept and feature coefficients for tabular risk estimation
    intercept: float = -6.5
    weights: tuple[float, float, float, float, float, float] = (
        0.045,  # Age
        0.035,  # BMI
        0.025,  # Systolic BP
        0.015,  # Fasting Glucose
        0.750,  # Smoker (binary)
        0.550,  # Family History (binary)
    )

    def predict_probability(self, features: Sequence[float]) -> float:
        """Calculate estimated risk probability using logistic function."""
        if len(features) < 6:
            raise ValueError(f"Expected 6 features, got {len(features)}")
        
        linear_combination = self.intercept
        for w, x in zip(self.weights, features):
            linear_combination += w * float(x)
            
        # Sigmoid function
        # Clamp to avoid math overflow
        linear_combination = max(-20.0, min(20.0, linear_combination))
        probability = 1.0 / (1.0 + math.exp(-linear_combination))
        return probability

