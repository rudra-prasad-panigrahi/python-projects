"""Produces an informational health brief from explicitly authorized facts."""
from .model import latest_facts

def create_health_brief(records: list[dict]) -> dict:
    facts = latest_facts(records)
    if not facts:
        return {"summary": "No source-backed health information is available to summarize.", "facts": [], "informational_only": True}
    lines = [f"{fact.label}: {fact.value}" for fact in facts]
    return {"summary": "Recent available records: " + "; ".join(lines) + ".", "facts": [fact.__dict__ for fact in facts], "informational_only": True, "disclaimer": "This is a summary of recorded information, not a diagnosis or treatment recommendation."}
