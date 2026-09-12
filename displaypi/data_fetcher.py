"""Background data fetching for weather, news, and historical events.

Each data source is polled on its own daemon thread and the results are
cached behind a lock so the display loop can read them safely.
"""

import threading
import time
import unicodedata

import feedparser
import requests

from . import config


WMO_WEATHER_CODES = {
    0: "clear skies",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy conditions",
    48: "rime fog",
    51: "light drizzle",
    53: "drizzle",
    55: "heavy drizzle",
    56: "freezing drizzle",
    57: "heavy freezing drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    66: "freezing rain",
    67: "heavy freezing rain",
    71: "light snow",
    73: "snow",
    75: "heavy snow",
    77: "snow grains",
    80: "light showers",
    81: "showers",
    82: "heavy showers",
    85: "light snow showers",
    86: "snow showers",
    95: "thunderstorms",
    96: "thunderstorms with hail",
    99: "heavy thunderstorms with hail",
}


class DataFetcher:
    """Fetches data in the background and exposes thread-safe snapshots."""

    def __init__(self):
        self.weather_data = {
            "temp_c": None,
            "temp_f": None,
            "feels_c": None,
            "feels_f": None,
            "humidity": None,
            "wind_mph": None,
            "wind_gusts_mph": None,
            "rain_chance": None,
        }
        self.news_headlines = []
        self.history_events = []
        self.word_of_day = {}

        self._lock = threading.Lock()

        self._start_threads()

    def _start_threads(self):
        jobs = [
            (self._update_weather_loop, config.WEATHER_UPDATE_INTERVAL),
            (self._update_news_loop, config.NEWS_UPDATE_INTERVAL),
            (self._update_history_loop, config.HISTORY_UPDATE_INTERVAL),
            (self._update_word_loop, config.WORD_UPDATE_INTERVAL),
        ]
        for target, _interval in jobs:
            thread = threading.Thread(target=target, daemon=True)
            thread.start()

    def get_weather(self):
        with self._lock:
            return self.weather_data.copy()

    def get_news(self):
        with self._lock:
            return list(self.news_headlines)

    def get_history(self):
        with self._lock:
            return list(self.history_events)

    def get_word_of_day(self):
        with self._lock:
            return dict(self.word_of_day)

    def _update_weather_loop(self):
        while True:
            try:
                self._refresh_weather()
            except Exception as exc:
                print(f"Weather fetch error: {exc}")
            time.sleep(config.WEATHER_UPDATE_INTERVAL)

    def _update_news_loop(self):
        while True:
            try:
                self._refresh_news()
            except Exception as exc:
                print(f"News fetch error: {exc}")
            time.sleep(config.NEWS_UPDATE_INTERVAL)

    def _update_history_loop(self):
        while True:
            try:
                self._refresh_history()
            except Exception as exc:
                print(f"History fetch error: {exc}")
            time.sleep(config.HISTORY_UPDATE_INTERVAL)

    def _update_word_loop(self):
        while True:
            try:
                self._refresh_word_of_day()
            except Exception as exc:
                print(f"Word of the day fetch error: {exc}")
            time.sleep(config.WORD_UPDATE_INTERVAL)

    def _refresh_weather(self):
        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={config.LATITUDE}&longitude={config.LONGITUDE}"
            "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
            "wind_speed_10m,wind_gusts_10m,precipitation_probability"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            f"&wind_speed_unit=mph&timezone={config.TIMEZONE}"
        )

        weather_resp = requests.get(weather_url, timeout=10)

        if weather_resp.status_code != 200:
            return

        self._store_weather(weather_resp.json())

    def _store_weather(self, weather_data):
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})

        forecast = self._parse_forecast(daily)

        updates = {
            "humidity": current.get("relative_humidity_2m"),
            "wind_mph": current.get("wind_speed_10m"),
            "wind_gusts_mph": current.get("wind_gusts_10m"),
            "rain_chance": current.get("precipitation_probability"),
            **forecast,
        }

        temp_c = current.get("temperature_2m")
        feels_c = current.get("apparent_temperature")

        with self._lock:
            if temp_c is not None:
                updates["temp_c"] = temp_c
                updates["temp_f"] = (temp_c * 9 / 5) + 32
            if feels_c is not None:
                updates["feels_c"] = feels_c
                updates["feels_f"] = (feels_c * 9 / 5) + 32
            self.weather_data.update(updates)

    def _parse_forecast(self, daily):
        if not daily or len(daily.get("time", [])) <= 1:
            return {
                "forecast_desc": "partly cloudy",
                "forecast_pop": None,
                "forecast_max_c": None,
                "forecast_min_c": None,
                "forecast_max_f": None,
                "forecast_min_f": None,
            }

        # Index 1 is tomorrow.
        code = daily.get("weather_code", [])[1]
        forecast_max_c = daily.get("temperature_2m_max", [])[1]
        forecast_min_c = daily.get("temperature_2m_min", [])[1]

        forecast = {
            "forecast_desc": WMO_WEATHER_CODES.get(code, "partly cloudy"),
            "forecast_pop": daily.get("precipitation_probability_max", [])[1],
            "forecast_max_c": forecast_max_c,
            "forecast_min_c": forecast_min_c,
        }
        if forecast_max_c is not None and forecast_min_c is not None:
            forecast["forecast_max_f"] = (forecast_max_c * 9 / 5) + 32
            forecast["forecast_min_f"] = (forecast_min_c * 9 / 5) + 32
        return forecast

    def _refresh_news(self):
        feed = feedparser.parse(config.RSS_FEED_URL)
        headlines = [
            self._sanitize_string(entry.title) for entry in feed.entries[: config.MAX_HEADLINES]
        ]

        if headlines:
            with self._lock:
                self.news_headlines = headlines

    def _refresh_history(self):
        resp = requests.get("https://api.dayinhistory.dev/v1/today/events/", timeout=10)
        if resp.status_code != 200:
            return

        events = []
        for item in resp.json().get("results", [])[:1]:
            year = item.get("year", "")
            title = item.get("title", "")
            events.append(f"In {year}: {title}")

        if events:
            with self._lock:
                self.history_events = events

    def _refresh_word_of_day(self):
        resp = requests.get(config.WORD_API_URL, timeout=10)
        if resp.status_code != 200:
            return

        data = resp.json()
        word = data.get("word")
        definition = data.get("definition") or data.get("meaning")
        if not word or not definition:
            return

        with self._lock:
            self.word_of_day = {
                "word": self._sanitize_string(word),
                "part_of_speech": self._sanitize_string(data.get("partOfSpeech", "")),
                "definition": self._sanitize_string(definition),
                "date": data.get("date", ""),
            }

    @staticmethod
    def _sanitize_string(text):
        """Reduce text to basic ASCII so the LED matrix can render it."""
        text = unicodedata.normalize("NFKD", text)
        return text.encode("ascii", "ignore").decode("ascii")