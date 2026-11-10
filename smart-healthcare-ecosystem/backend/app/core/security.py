from pathlib import Path
from uuid import uuid4

def safe_storage_name(filename: str) -> str:
    """Avoid path traversal and preserve only a harmless suffix."""
    suffix = Path(filename).suffix.lower()
    return f"{uuid4().hex}{suffix}"
