"""Application configuration and constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COUNTDOWNS_FILE = DATA_DIR / "countdowns.json"

# --- Display Settings ---
CASCADED_MATRICES = 28
BLOCK_ORIENTATION = -90  # Default for most 4-in-1 modules. Change to 90 or 0 if scrolling is wrong.
SCROLL_DELAY = 0.015
BRIGHTNESS = 128  # 0 to 255

# --- Weather Settings ---
LATITUDE = 42.4184  # Medford, MA
LONGITUDE = -71.1062
TIMEZONE = "auto"
WEATHER_UPDATE_INTERVAL = 900  # 15 minutes

# --- News Settings ---
RSS_FEED_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
MAX_HEADLINES = 5
NEWS_UPDATE_INTERVAL = 3600  # 1 hour

# --- History Settings ---
HISTORY_UPDATE_INTERVAL = 43200  # 12 hours

# --- OTA Update Settings ---
UPDATE_CHECK_INTERVAL = 60  # seconds between git update checks

# --- Countdown Lock Settings ---
COUNTDOWN_LOCK_WINDOW_SECONDS = 3600  # < 1 hour: lock the display