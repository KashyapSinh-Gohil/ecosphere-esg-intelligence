"""Vercel ASGI entry point for the EcoSphere FastAPI application."""
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DATABASE = Path("/tmp/ecosphere_esg.db")
SEEDED_DATABASE = ROOT / "ecosphere_esg.db"

if not RUNTIME_DATABASE.exists() and SEEDED_DATABASE.exists():
    shutil.copy2(SEEDED_DATABASE, RUNTIME_DATABASE)

os.environ.setdefault("DATABASE_URL", f"sqlite:///{RUNTIME_DATABASE}")

from backend.app.main import app  # noqa: E402,F401
