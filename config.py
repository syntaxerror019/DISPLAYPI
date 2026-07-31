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
# Dictionary of countdowns: "Name": datetime object
# Add or remove events as needed
COUNTDOWNS = {
    "Xmas": datetime.datetime(datetime.datetime.now().year, 12, 25),
    "New Year": datetime.datetime(datetime.datetime.now().year + 1, 1, 1),
}
# Make sure countdowns are in the future
for name in list(COUNTDOWNS.keys()):
    if COUNTDOWNS[name] < datetime.datetime.now():
        # Move to next year if it already passed
        COUNTDOWNS[name] = COUNTDOWNS[name].replace(year=COUNTDOWNS[name].year + 1)
