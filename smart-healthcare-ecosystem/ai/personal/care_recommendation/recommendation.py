from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class CareOption:
    id: str
    name: str
    service_type: str
    specialty: str | None = None
    distance_km: float | None = None
    rating: float | None = None
    availability_score: float | None = None
    quality_score: float | None = None


class CareRecommendationEngine:
    """
    Ranks healthcare options using transparent, configurable scoring.

    This is a care-navigation/recommendation component.
    It must not be presented as a medical diagnosis engine.
    """

    def __init__(
        self,
        distance_weight: float = 0.35,
        rating_weight: float = 0.20,
        availability_weight: float = 0.20,
        quality_weight: float = 0.25,
    ) -> None:
        total = (
            distance_weight
            + rating_weight
            + availability_weight
            + quality_weight
        )

        if total <= 0:
            raise ValueError(
                "Recommendation weights must sum to a positive value."
            )

        self.distance_weight = distance_weight / total
        self.rating_weight = rating_weight / total
        self.availability_weight = availability_weight / total
        self.quality_weight = quality_weight / total

    @staticmethod
    def _normalize(
        value: float | None,
        minimum: float,
        maximum: float,
    ) -> float:
        if value is None or maximum <= minimum:
            return 0.0

        bounded = min(max(float(value), minimum), maximum)
        return (bounded - minimum) / (maximum - minimum)

    def score(self, option: CareOption) -> float:
        distance_score = 1.0 - self._normalize(
            option.distance_km,
            0.0,
            100.0,
        )

        rating_score = self._normalize(
            option.rating,
            0.0,
            5.0,
        )

        availability_score = self._normalize(
            option.availability_score,
            0.0,
            1.0,
        )

        quality_score = self._normalize(
            option.quality_score,
            0.0,
            1.0,
        )

        score = (
            distance_score * self.distance_weight
            + rating_score * self.rating_weight
            + availability_score * self.availability_weight
            + quality_score * self.quality_weight
        )

        return round(score, 4)

    def recommend(
        self,
        options: Iterable[CareOption],
        service_type: str | None = None,
        specialty: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be at least 1.")

        filtered: list[CareOption] = []

        for option in options:
            if (
                service_type
                and option.service_type.lower()
                != service_type.lower()
            ):
                continue

            if (
                specialty
                and (
                    option.specialty is None
                    or option.specialty.lower()
                    != specialty.lower()
                )
            ):
                continue

            filtered.append(option)

        ranked = sorted(
            filtered,
            key=self.score,
            reverse=True,
        )

        return [
            {
                "id": option.id,
                "name": option.name,
                "service_type": option.service_type,
                "specialty": option.specialty,
                "recommendation_score": self.score(option),
                "distance_km": option.distance_km,
                "rating": option.rating,
                "availability_score": option.availability_score,
                "quality_score": option.quality_score,
            }
            for option in ranked[:limit]
        ]