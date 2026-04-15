from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
ASSET_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "hospital_records.db"
HOSPITAL_NAME = "CITY GENERAL HOSPITAL"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"