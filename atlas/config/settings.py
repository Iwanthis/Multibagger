from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data
DATA_DIR = PROJECT_ROOT / "data"

UNIVERSE_DIR = DATA_DIR / "universe"

MARKET_DATA_DIR = DATA_DIR / "market_data"

DAILY_DATA_DIR = MARKET_DATA_DIR / "daily"

WEEKLY_DATA_DIR = MARKET_DATA_DIR / "weekly"

MONTHLY_DATA_DIR = MARKET_DATA_DIR / "monthly"

CACHE_DIR = DATA_DIR / "cache"

EXPORT_DIR = DATA_DIR / "exports"

LOG_DIR = DATA_DIR / "logs"

SCAN_DIR = DATA_DIR / "scans"

REPORTS_DIR = DATA_DIR / "reports"

HISTORY_DIR = DATA_DIR / "history"

WATCHLISTS_DIR = DATA_DIR / "watchlists"