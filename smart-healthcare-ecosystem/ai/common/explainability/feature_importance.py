from __future__ import annotations

from typing import Any

import numpy as np


def feature_importance(
    model: Any,
    feature_names: list[str],
) -> list[dict[str, float | str]]:
    """
    Works with estimators exposing feature_importances_.

    For models that do not expose it, SHAP can be integrated later.
    """

    if not hasattr(
        model,
        "feature_importances_",
    ):
        raise TypeError(
            "Model does not expose feature_importances_."
        )

    importances = np.asarray(
        model.feature_importances_,
        dtype=float,
    )

    if len(importances) != len(feature_names):
        raise ValueError(
            "Feature-name count does not match model feature count."
        )

    result = [
        {
            "feature": name,
            "importance": float(value),
        }
        for name, value in zip(
            feature_names,
            importances,
        )
    ]

    result.sort(
        key=lambda item: float(item["importance"]),
        reverse=True,
    )

    return result