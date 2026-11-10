from .config import settings

def enabled(name: str) -> bool:
    return {"development_demo_auth": settings.demo_auth_enabled, "document_upload": True, "ai_assistant": True}.get(name, False)
