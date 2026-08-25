"""
Application configuration.

All configuration is read from environment variables (see .env.example at the
project root). No secrets are hardcoded anywhere in this file.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    # Loads a .env file into os.environ if python-dotenv is installed.
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
DEMO_DIR = DATA_DIR / "demo"
SAMPLE_DATA_DIR = DATA_DIR / "sample_data"


class Settings:
    """Centralized, environment-driven settings object."""

    # --- General ---
    DEMO_MODE: bool = _bool(os.getenv("DEMO_MODE"), default=True)
    APP_NAME: str = "DisasterGraph AI"
    APP_VERSION: str = "1.0.0"

    # --- LLM (OpenAI-compatible) ---
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

    # --- Neo4j ---
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")

    # --- Chroma ---
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", str(BASE_DIR / "data" / "chroma_store"))

    # --- SQLite ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")
    SQLITE_PATH: str = str(BASE_DIR / "data" / "app.db")

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()
    ]

    # --- Upload limits ---
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
    ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}


settings = Settings()

# Ensure required data directories exist at import time.
for _d in (DATA_DIR, DOCUMENTS_DIR, DEMO_DIR, SAMPLE_DATA_DIR, Path(settings.CHROMA_PATH)):
    _d.mkdir(parents=True, exist_ok=True)
