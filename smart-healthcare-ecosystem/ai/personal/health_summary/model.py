"""Safe, deterministic summary primitives for authorized personal health data."""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class SummaryFact:
    label: str
    value: str
    occurred_at: datetime | None = None
    source: str | None = None

def latest_facts(records: list[dict], limit: int = 5) -> list[SummaryFact]:
    """Select source-backed facts only; it never infers diagnoses or missing values."""
    ranked = sorted(records, key=lambda r: r.get("occurred_at", ""), reverse=True)
    return [SummaryFact(str(r.get("label", "Health record")), str(r.get("value", "Unavailable")), r.get("occurred_at"), r.get("source")) for r in ranked[:limit] if r.get("source")]
