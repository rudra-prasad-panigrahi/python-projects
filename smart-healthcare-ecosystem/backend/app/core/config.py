from dataclasses import dataclass
from os import getenv

@dataclass(frozen=True)
class Settings:
    environment: str = getenv("APP_ENV", "development")
    database_url: str = getenv("DATABASE_URL", "sqlite:///./personal-health.db")
    storage_root: str = getenv("STORAGE_ROOT", "./storage")
    demo_auth_enabled: bool = getenv("ENABLE_DEMO_AUTH", "false").lower() == "true"
    max_document_bytes: int = int(getenv("MAX_DOCUMENT_BYTES", str(10 * 1024 * 1024)))
    frontend_url: str = getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    backend_public_url: str = getenv("BACKEND_PUBLIC_URL", "http://localhost:8000").rstrip("/")
    oauth_session_secret: str = getenv("OAUTH_SESSION_SECRET", "development-only-change-before-deployment")
    google_oauth_client_id: str = getenv("GOOGLE_OAUTH_CLIENT_ID", "")
    google_oauth_client_secret: str = getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
    github_oauth_client_id: str = getenv("GITHUB_OAUTH_CLIENT_ID", "")
    github_oauth_client_secret: str = getenv("GITHUB_OAUTH_CLIENT_SECRET", "")

settings = Settings()

if settings.environment.lower() == "production" and (
    settings.oauth_session_secret == "development-only-change-before-deployment"
    or settings.oauth_session_secret.startswith("replace-with-")
    or len(settings.oauth_session_secret) < 32
):
    raise RuntimeError("Set OAUTH_SESSION_SECRET to a unique secret of at least 32 characters in production.")
