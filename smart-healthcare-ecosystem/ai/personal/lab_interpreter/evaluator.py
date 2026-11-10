"""Validates that lab interpretations preserve source bounds and safety labels."""
def evaluate_interpretation(result: dict) -> dict:
    missing = [name for name in ("informational_only", "source", "result") if name not in result]
    contains_diagnosis = any(word in str(result.get("explanation", "")).lower() for word in ("diagnosed", "you have", "treat with"))
    return {"passes": not missing and not contains_diagnosis, "missing_fields": missing, "contains_diagnostic_language": contains_diagnosis}
