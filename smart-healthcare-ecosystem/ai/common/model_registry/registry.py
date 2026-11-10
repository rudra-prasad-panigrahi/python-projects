from __future__ import annotations

import json
from pathlib import Path

from .metadata import ModelMetadata


class ModelRegistry:
    def __init__(
        self,
        registry_path: str | Path = "model_registry.json",
    ) -> None:
        self.registry_path = Path(registry_path)

    def _read(self) -> dict:
        if not self.registry_path.exists():
            return {}

        try:
            return json.loads(
                self.registry_path.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid model registry: {self.registry_path}"
            ) from exc

    def _write(self, data: dict) -> None:
        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.registry_path.write_text(
            json.dumps(
                data,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

    def register(
        self,
        metadata: ModelMetadata,
    ) -> None:
        data = self._read()

        versions = data.setdefault(
            metadata.name,
            {},
        )

        versions[metadata.version] = (
            metadata.model_dump(mode="json")
        )

        self._write(data)

    def get(
        self,
        name: str,
        version: str,
    ) -> ModelMetadata | None:
        data = self._read()

        raw = (
            data
            .get(name, {})
            .get(version)
        )

        if raw is None:
            return None

        return ModelMetadata.model_validate(raw)

    def latest(
        self,
        name: str,
    ) -> ModelMetadata | None:
        data = self._read()

        versions = data.get(
            name,
            {},
        )

        if not versions:
            return None

        version = sorted(
            versions.keys()
        )[-1]

        return ModelMetadata.model_validate(
            versions[version]
        )