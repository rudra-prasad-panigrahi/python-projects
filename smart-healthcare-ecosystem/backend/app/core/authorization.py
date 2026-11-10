from .exceptions import forbidden

def require_owner(requested_user_id: str, authenticated_user_id: str) -> None:
    """Enforce the personal-data boundary before retrieval or mutation."""
    if requested_user_id != authenticated_user_id:
        raise forbidden()
