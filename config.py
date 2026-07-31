import datetime

# --- Display Settings ---
CASCADED_MATRICES = 12
BLOCK_ORIENTATION = -90  # Default for most 4-in-1 modules. Change to 90 or 0 if scrolling is wrong.
SCROLL_DELAY = 0.04
BRIGHTNESS = 128  # 0 to 255

# --- Weather Settings ---
# Coordinates for Open-Meteo (Defaulting to New York City for example)
# Replace with your desired latitude and longitude
LATITUDE = 40.7128
LONGITUDE = -74.0060
TIMEZONE = "auto"
# Weather update interval in seconds
WEATHER_UPDATE_INTERVAL = 900  # 15 minutes

# --- News Settings ---
# Google News RSS
RSS_FEED_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
# Number of headlines to display per cycle
MAX_HEADLINES = 5
# News update interval in seconds
NEWS_UPDATE_INTERVAL = 3600  # 1 hour

# --- Countdowns ---
# Dictionary of holidays: "Name": (Month, Day)
# For holidays without fixed dates (like Thanksgiving), we can approximate or use fixed ones for now
HOLIDAYS = {
    "New Year": (1, 1),
    "V-Day": (2, 14),
    "St Pat": (3, 17),
    "July 4": (7, 4),
    "Hween": (10, 31),
    "Xmas": (12, 25),
}
