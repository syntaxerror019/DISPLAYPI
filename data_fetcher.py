import threading
import time
import requests
import feedparser
import config

class DataFetcher:
    def __init__(self):
        self.weather_data = {"temp": None, "desc": None}
        self.news_headlines = []
        
        self._lock = threading.Lock()
        
        # Start daemon threads
        self.weather_thread = threading.Thread(target=self._update_weather_loop, daemon=True)
        self.news_thread = threading.Thread(target=self._update_news_loop, daemon=True)
        
        self.weather_thread.start()
        self.news_thread.start()

    def get_weather(self):
        with self._lock:
            return self.weather_data.copy()
            
    def get_news(self):
        with self._lock:
            return list(self.news_headlines)

    def _update_weather_loop(self):
        while True:
            try:
                # Open-Meteo free API
                url = f"https://api.open-meteo.com/v1/forecast?latitude={config.LATITUDE}&longitude={config.LONGITUDE}&current=temperature_2m,weather_code&temperature_unit=fahrenheit&timezone={config.TIMEZONE}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current", {})
                    temp = current.get("temperature_2m")
                    code = current.get("weather_code", 0)
                    desc = self._wmo_code_to_desc(code)
                    
                    with self._lock:
                        self.weather_data["temp"] = temp
                        self.weather_data["desc"] = desc
            except Exception as e:
                print(f"Weather fetch error: {e}")
                
            time.sleep(config.WEATHER_UPDATE_INTERVAL)

    def _update_news_loop(self):
        while True:
            try:
                feed = feedparser.parse(config.RSS_FEED_URL)
                headlines = []
                for entry in feed.entries[:config.MAX_HEADLINES]:
                    headlines.append(entry.title)
                
                if headlines:
                    with self._lock:
                        self.news_headlines = headlines
            except Exception as e:
                print(f"News fetch error: {e}")
                
            time.sleep(config.NEWS_UPDATE_INTERVAL)
            
    def _wmo_code_to_desc(self, code):
        # WMO Weather interpretation codes
        # https://open-meteo.com/en/docs
        wmo_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light Drizzle",
            53: "Moderate Drizzle",
            55: "Dense Drizzle",
            56: "Light Freezing Drizzle",
            57: "Dense Freezing Drizzle",
            61: "Slight Rain",
            63: "Moderate Rain",
            65: "Heavy Rain",
            66: "Light Freezing Rain",
            67: "Heavy Freezing Rain",
            71: "Slight Snow",
            73: "Moderate Snow",
            75: "Heavy Snow",
            77: "Snow grains",
            80: "Slight Rain showers",
            81: "Moderate Rain showers",
            82: "Violent Rain showers",
            85: "Slight Snow showers",
            86: "Heavy Snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return wmo_codes.get(code, "Unknown")
