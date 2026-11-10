"""Lightweight safety checks for generated health briefs."""
UNSAFE_TERMS = {"diagnosis", "prescribe", "treatment plan", "you have"}

def evaluate_summary(summary: dict) -> dict:
    text = summary.get("summary", "").lower()
    missing_sources = [fact for fact in summary.get("facts", []) if not fact.get("source")]
    return {"passes": not any(term in text for term in UNSAFE_TERMS) and not missing_sources, "missing_source_count": len(missing_sources), "informational_only": summary.get("informational_only") is True}
