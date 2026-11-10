SENSITIVE_SCOPES = {"profile", "records", "laboratory", "medications", "documents", "emergency"}

def is_scope_allowed(requested: set[str], granted: set[str]) -> bool:
    """An empty grant never authorizes sensitive data."""
    return requested.issubset(granted) and requested.issubset(SENSITIVE_SCOPES)
