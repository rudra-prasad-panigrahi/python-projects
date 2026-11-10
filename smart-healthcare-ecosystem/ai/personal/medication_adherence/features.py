from __future__ import annotations

from datetime import datetime
from typing import Any

FEATURE_COLUMNS = [
    "days_in_period",
    "doses_scheduled",
    "doses_taken",
    "missed_doses",
    "late_doses",
    "days_since_last_missed",
]


def parse_date(d: Any) -> datetime | None:
    if isinstance(d, datetime):
        return d
    if isinstance(d, str):
        try:
            return datetime.fromisoformat(d.replace("Z", "+00:00"))
        except Exception:
            try:
                return datetime.strptime(d[:10], "%Y-%m-%d")
            except Exception:
                return None
    return None


def build_adherence_features(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    if not events:
        return {
            "days_in_period": 0,
            "doses_scheduled": 0,
            "doses_taken": 0,
            "missed_doses": 0,
            "late_doses": 0,
            "days_since_last_missed": 0,
        }

    valid_events = []
    for ev in events:
        dt = parse_date(ev.get("date") or ev.get("occurred_at") or ev.get("recorded_at"))
        if dt is not None:
            valid_events.append({
                "date": dt,
                "scheduled": bool(ev.get("scheduled", True)),
                "taken": bool(ev.get("taken", False)),
                "late": bool(ev.get("late", False)),
            })

    if not valid_events:
        return {
            "days_in_period": 0,
            "doses_scheduled": 0,
            "doses_taken": 0,
            "missed_doses": 0,
            "late_doses": 0,
            "days_since_last_missed": 0,
        }

    dates = [e["date"] for e in valid_events]
    min_date = min(dates)
    max_date = max(dates)
    period_days = max(1, (max_date.date() - min_date.date()).days + 1)

    scheduled = sum(1 for e in valid_events if e["scheduled"])
    taken = sum(1 for e in valid_events if e["scheduled"] and e["taken"])
    late = sum(1 for e in valid_events if e["scheduled"] and e["late"])
    missed = max(0, scheduled - taken)

    missed_dates = [e["date"] for e in valid_events if e["scheduled"] and not e["taken"]]
    if not missed_dates:
        days_since_last_missed = period_days
    else:
        days_since_last_missed = max(0, (max_date.date() - max(missed_dates).date()).days)

    return {
        "days_in_period": period_days,
        "doses_scheduled": scheduled,
        "doses_taken": taken,
        "missed_doses": missed,
        "late_doses": late,
        "days_since_last_missed": days_since_last_missed,
    }