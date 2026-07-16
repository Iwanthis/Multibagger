from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

UNIVERSE_DIR = DATA_DIR / "universe"

MARKET_DATA_DIR = DATA_DIR / "market_data"
DAILY_DATA_DIR = MARKET_DATA_DIR / "daily"

EXPORT_DIR = DATA_DIR / "exports"
SCAN_DIR = DATA_DIR / "scans"
LOG_DIR = DATA_DIR / "logs"