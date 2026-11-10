from dataclasses import asdict, dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Provenance:
    source: str
    source_date: str | None = None
    imported_at: str | None = None
    verification_state: str = "unverified"
    document_reference: str | None = None
    ai_derived: bool = False

    def to_dict(self) -> dict:
        data = asdict(self)
        return {**data, "imported_at": data["imported_at"] or datetime.now(timezone.utc).isoformat()}
