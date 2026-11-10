from pathlib import Path
from ...core.security import safe_storage_name

class LocalStorage:
    def __init__(self, root: str): self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def save(self, filename: str, content: bytes) -> str:
        name = safe_storage_name(filename); (self.root / name).write_bytes(content); return name
