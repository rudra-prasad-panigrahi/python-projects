from __future__ import annotations

from typing import Any


def rank_care_options(
    options: list[dict[str, Any]],
    *,
    distance_weight: float = 0.35,
    rating_weight: float = 0.20,
    availability_weight: float = 0.20,
    quality_weight: float = 0.25,
) -> list[dict[str, Any]]:
    weights = {
        "distance": distance_weight,
        "rating": rating_weight,
        "availability": availability_weight,
        "quality": quality_weight,
    }

    total = sum(weights.values())

    if total <= 0:
        raise ValueError("Ranking weights must be positive.")

    def normalize(
        value: float | int | None,
        minimum: float,
        maximum: float,
    ) -> float:
        if value is None or maximum <= minimum:
            return 0.0

        bounded = min(
            max(float(value), minimum),
            maximum,
        )

        return (bounded - minimum) / (maximum - minimum)

    def calculate_score(option: dict[str, Any]) -> float:
        distance_score = 1.0 - normalize(
            option.get("distance_km"),
            0.0,
            100.0,
        )

        rating_score = normalize(
            option.get("rating"),
            0.0,
            5.0,
        )

        availability_score = normalize(
            option.get("availability_score"),
            0.0,
            1.0,
        )

        quality_score = normalize(
            option.get("quality_score"),
            0.0,
            1.0,
        )

        score = (
            distance_score * weights["distance"]
            + rating_score * weights["rating"]
            + availability_score * weights["availability"]
            + quality_score * weights["quality"]
        )

        return score / total

    ranked: list[dict[str, Any]] = []

    for option in options:
        result = dict(option)

        result["recommendation_score"] = round(
            calculate_score(option),
            4,
        )

        ranked.append(result)

    ranked.sort(
        key=lambda item: item["recommendation_score"],
        reverse=True,
    )

    for position, item in enumerate(
        ranked,
        start=1,
    ):
        item["rank"] = position

    return ranked