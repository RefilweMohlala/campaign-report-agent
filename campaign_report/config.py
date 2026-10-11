"""Settings, read from the .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent   # the project folder
load_dotenv(ROOT / ".env")

RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "output"
TEMPLATES_DIR = ROOT / "templates"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
USE_LLM = os.getenv("USE_LLM", "false").strip().lower() == "true"