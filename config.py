"""Configuration: reads settings and API keys from a .env file or environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _load_env_file(path):
    """Tiny .env reader (File Handling) so no extra library is needed."""
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BASE_DIR / ".env")

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "").strip()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM = os.getenv("TWILIO_FROM", "").strip()
ALERT_TO = os.getenv("ALERT_TO", "").strip()

# Each API falls back to demo data when its key is missing (or FORCE_DEMO=true).
FORCE_DEMO = os.getenv("FORCE_DEMO", "false").lower() == "true"
STOCK_DEMO = FORCE_DEMO or not ALPHA_VANTAGE_KEY
NEWS_DEMO = FORCE_DEMO or not NEWS_API_KEY
SMS_ENABLED = all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, ALERT_TO]) and not FORCE_DEMO

PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD", "2.0"))   # percent move that triggers news fetch
NEWS_LIMIT = int(os.getenv("NEWS_LIMIT", "3"))                 # articles per stock
HIGH_IMPACT = float(os.getenv("HIGH_IMPACT", "0.5"))           # |sentiment| needed for an alert
REQUEST_TIMEOUT = 15
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "stock_news.db"))
