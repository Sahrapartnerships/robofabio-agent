"""Configuration for TikTok Poster Bot."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
LOGS_DIR = DATA_DIR / "logs"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

# Create directories if they don't exist
for dir_path in [DATA_DIR, SESSIONS_DIR, LOGS_DIR, SCREENSHOTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# TikTok URLs
TIKTOK_URL = "https://www.tiktok.com"
TIKTOK_LOGIN_URL = "https://www.tiktok.com/login"
TIKTOK_UPLOAD_URL = "https://www.tiktok.com/creator-center/upload"

# Browser settings
HEADLESS = os.getenv("TIKTOK_HEADLESS", "true").lower() == "true"
BROWSER_TYPE = os.getenv("TIKTOK_BROWSER", "chromium")  # chromium, firefox, webkit
SLOW_MO = int(os.getenv("TIKTOK_SLOW_MO", "0"))  # Slow motion delay in ms (for debugging)

# Timeouts (in milliseconds)
DEFAULT_TIMEOUT = int(os.getenv("TIKTOK_TIMEOUT", "30000"))
NAVIGATION_TIMEOUT = int(os.getenv("TIKTOK_NAV_TIMEOUT", "60000"))
UPLOAD_TIMEOUT = int(os.getenv("TIKTOK_UPLOAD_TIMEOUT", "300000"))  # 5 minutes for uploads

# Retry settings
MAX_RETRIES = int(os.getenv("TIKTOK_MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("TIKTOK_RETRY_DELAY", "5"))  # seconds between retries

# Delay settings (in seconds)
DELAYS = {
    "min": float(os.getenv("TIKTOK_DELAY_MIN", "2")),
    "max": float(os.getenv("TIKTOK_DELAY_MAX", "5")),
    "typing_min": float(os.getenv("TIKTOK_TYPING_MIN", "0.05")),
    "typing_max": float(os.getenv("TIKTOK_TYPING_MAX", "0.15")),
}

# Post settings
MAX_IMAGES_PER_CAROUSEL = 35  # TikTok's maximum
MAX_CAPTION_LENGTH = 2200  # TikTok's maximum caption length

# Scheduler settings (optional)
SCHEDULER_ENABLED = os.getenv("TIKTOK_SCHEDULER", "false").lower() == "true"
SCHEDULER_DB_PATH = DATA_DIR / "schedule.db"

# Logging
LOG_LEVEL = os.getenv("TIKTOK_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Credentials (use environment variables or .env file)
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "")
TIKTOK_PASSWORD = os.getenv("TIKTOK_PASSWORD", "")
TIKTOK_EMAIL = os.getenv("TIKTOK_EMAIL", "")

# Session settings
SESSION_FILE = SESSIONS_DIR / "tiktok_session.json"
SESSION_STORAGE_FILE = SESSIONS_DIR / "tiktok_storage_state.json"
SESSION_EXPIRY_DAYS = int(os.getenv("TIKTOK_SESSION_EXPIRY", "7"))

# User Agent (use a recent Chrome on Windows)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Viewport settings
VIEWPORT = {
    "width": 1920,
    "height": 1080,
}

# Feature flags
USE_STEALTH = os.getenv("TIKTOK_STEALTH", "true").lower() == "true"
SAVE_SCREENSHOTS = os.getenv("TIKTOK_SCREENSHOTS", "true").lower() == "true"
DEBUG_MODE = os.getenv("TIKTOK_DEBUG", "false").lower() == "true"
