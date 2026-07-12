"""Vercel ASGI entry point for the EcoSphere FastAPI application."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DATABASE = Path("/tmp/ecosphere_esg.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{RUNTIME_DATABASE}")

from backend.app.main import app  # noqa: E402,F401
