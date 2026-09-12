"""Application configuration and constants."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COUNTDOWNS_FILE = DATA_DIR / "countdowns.json"


def _load_env_file(path):
    """Load KEY=VALUE pairs from an optional .env file into the environment.

    Existing environment variables take precedence so real deployments can
    override the file without editing it.
    """
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(PROJECT_ROOT / ".env")

# --- Display Settings ---
CASCADED_MATRICES = 20
BLOCK_ORIENTATION = -90  # Default for most 4-in-1 modules. Change to 90 or 0 if scrolling is wrong.
DISPLAY_ROTATE = 2  # 0=0°, 1=90°, 2=180°, 3=270°
SCROLL_DELAY = 0.012
BRIGHTNESS = 150  # 0 to 255

# --- Weather Settings ---
LATITUDE = 42.419331
LONGITUDE = -71.119720
TIMEZONE = "auto"
WEATHER_UPDATE_INTERVAL = 900  # 15 minutes

# --- News Settings ---
RSS_FEED_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
MAX_HEADLINES = 5
NEWS_UPDATE_INTERVAL = 3600  # 1 hour

# --- History Settings ---
HISTORY_UPDATE_INTERVAL = 43200  # 12 hours
HISTORY_EVERY_N_LOOPS = 2  # how many main-loop cycles between "On This Day" displays

# --- Word of the Day Settings ---
WORD_API_URL = "https://wordoftheday.freeapi.me/"
WORD_UPDATE_INTERVAL = 3600  # 1 hour
WORD_EVERY_N_LOOPS = 2  # how many main-loop cycles between word-of-the-day displays

# --- Countdown Display Settings ---
COUNTDOWN_EVERY_N_LOOPS = 4  # how many main-loop cycles between countdown reminders

# --- OTA Update Settings ---
UPDATE_CHECK_INTERVAL = 60  # seconds between git update checks

# --- Countdown Lock Settings ---
COUNTDOWN_LOCK_WINDOW_SECONDS = 3600  # < 1 hour: lock the display to the countdown (e.g. new years!!)

# --- MBTA Bus Settings ---
MBTA_API_KEY = os.environ.get("MBTA_API_KEY", "")
MBTA_STOP_ID = 5034
MBTA_ROUTE_ID = 101
MBTA_PREDICTIONS_URL = "https://api-v3.mbta.com/predictions"
MBTA_POLL_INTERVAL = 30  # seconds between bus arrival refreshes
MBTA_MAX_BUSES = 3  # how many upcoming buses to show
MBTA_WINDOW_START = "06:30"
MBTA_WINDOW_END = "07:30"

# --- Debug Settings ---
DEBUG = True  # set to False to quiet the console logs