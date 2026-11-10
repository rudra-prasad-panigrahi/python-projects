from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    resource: str
    occurred_at: str
    purpose: str | None = None

def build_audit_event(actor: str, action: str, resource: str, purpose: str | None = None) -> AuditEvent:
    return AuditEvent(actor, action, resource, datetime.now(timezone.utc).isoformat(), purpose)
