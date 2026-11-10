from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PredictionLogger:
    """
    Lightweight local prediction logger.

    Do not log sensitive personal health data.
    Store only technical metadata and non-sensitive identifiers.
    """

    def __init__(
        self,
        path: str | Path = "prediction_logs.jsonl",
    ) -> None:
        self.path = Path(path)

    def log(
        self,
        *,
        model_name: str,
        model_version: str,
        request_id: str,
        latency_ms: float,
        prediction: Any,
        confidence: float | None = None,
    ) -> None:
        record = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "model_name": model_name,
            "model_version": model_version,
            "request_id": request_id,
            "latency_ms": round(
                latency_ms,
                3,
            ),
            "prediction": prediction,
        }

        if confidence is not None:
            record["confidence"] = round(
                confidence,
                6,
            )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(
                    record,
                    default=str,
                )
                + "\n"
            )