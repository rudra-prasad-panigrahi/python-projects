from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


def load_model(
    path: str | Path,
) -> Any:
    model_path = Path(path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {model_path}"
        )

    return joblib.load(model_path)