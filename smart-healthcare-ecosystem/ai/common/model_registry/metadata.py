from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    name: str
    version: str
    task: str
    framework: str
    metrics: dict[str, float] = Field(
        default_factory=dict
    )
    artifact_path: str
    dataset_version: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    description: str = ""