import threading
import time
import requests
import feedparser
import config
import unicodedata

class DataFetcher:
    def __init__(self):
        self.weather_data = {
            "temp_c": None, "temp_f": None,
            "feels_c": None, "feels_f": None,
            "humidity": None,
            "wind_mph": None,
            "pollen": None
        }
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

    def _sanitize_string(self, text):
        """Removes smart quotes and unsupported unicode characters."""
        # Normalize unicode to closest ASCII representation (e.g. smart quotes to standard quotes)
        text = unicodedata.normalize('NFKD', text)
        # Keep only standard ASCII (0-127), ignore the rest
        text = text.encode('ascii', 'ignore').decode('ascii')
        return text

    def _update_weather_loop(self):
        while True:
            try:
                # 1. Fetch main weather (including daily forecast for tomorrow)
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={config.LATITUDE}&longitude={config.LONGITUDE}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&wind_speed_unit=mph&timezone={config.TIMEZONE}"
                w_resp = requests.get(w_url, timeout=10)
                
                # 2. Fetch pollen (Air Quality API)
                p_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={config.LATITUDE}&longitude={config.LONGITUDE}&current=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen&timezone={config.TIMEZONE}"
                p_resp = requests.get(p_url, timeout=10)
                
                if w_resp.status_code == 200 and p_resp.status_code == 200:
                    w_data = w_resp.json()
                    p_data = p_resp.json()
                    
                    # Current weather
                    current = w_data.get("current", {})
                    temp_c = current.get("temperature_2m")
                    feels_c = current.get("apparent_temperature")
                    humidity = current.get("relative_humidity_2m")
                    wind = current.get("wind_speed_10m")
                    
                    # Forecast (index 1 is tomorrow)
                    daily = w_data.get("daily", {})
                    if daily and len(daily.get("time", [])) > 1:
                        forecast_code = daily.get("weather_code", [])[1]
                        forecast_desc = self._wmo_code_to_desc(forecast_code)
                        forecast_max_c = daily.get("temperature_2m_max", [])[1]
                        forecast_min_c = daily.get("temperature_2m_min", [])[1]
                        forecast_pop = daily.get("precipitation_probability_max", [])[1]
                    else:
                        forecast_desc = "Unknown"
                        forecast_max_c = None
                        forecast_min_c = None
                        forecast_pop = None
                    
                    p_current = p_data.get("current", {})
                    # Sum all pollen types
                    pollen_sum = sum([
                        p_current.get("alder_pollen", 0) or 0,
                        p_current.get("birch_pollen", 0) or 0,
                        p_current.get("grass_pollen", 0) or 0,
                        p_current.get("mugwort_pollen", 0) or 0,
                        p_current.get("olive_pollen", 0) or 0,
                        p_current.get("ragweed_pollen", 0) or 0
                    ])
                    
                    # Basic heuristic for pollen severity
                    if pollen_sum < 10:
                        pollen_level = "Low"
                    elif pollen_sum < 50:
                        pollen_level = "Medium"
                    else:
                        pollen_level = "High"
                        
                    with self._lock:
                        if temp_c is not None:
                            self.weather_data["temp_c"] = temp_c
                            self.weather_data["temp_f"] = (temp_c * 9/5) + 32
                        if feels_c is not None:
                            self.weather_data["feels_c"] = feels_c
                            self.weather_data["feels_f"] = (feels_c * 9/5) + 32
                            
                        self.weather_data["humidity"] = humidity
                        self.weather_data["wind_mph"] = wind
                        self.weather_data["pollen"] = pollen_level
                        
                        # Store forecast
                        self.weather_data["forecast_desc"] = forecast_desc
                        self.weather_data["forecast_pop"] = forecast_pop
                        if forecast_max_c is not None and forecast_min_c is not None:
                            self.weather_data["forecast_max_f"] = (forecast_max_c * 9/5) + 32
                            self.weather_data["forecast_min_f"] = (forecast_min_c * 9/5) + 32
                        
            except Exception as e:
                print(f"Weather fetch error: {e}")
                
            time.sleep(config.WEATHER_UPDATE_INTERVAL)

    def _update_news_loop(self):
        while True:
            try:
                feed = feedparser.parse(config.RSS_FEED_URL)
                headlines = []
                for entry in feed.entries[:config.MAX_HEADLINES]:
                    sanitized_title = self._sanitize_string(entry.title)
                    headlines.append(sanitized_title)
                
                if headlines:
                    with self._lock:
                        self.news_headlines = headlines
            except Exception as e:
                print(f"News fetch error: {e}")
                
            time.sleep(config.NEWS_UPDATE_INTERVAL)

    def _wmo_code_to_desc(self, code):
        wmo_codes = {
            0: "Clear", 1: "M. Clear", 2: "P. Cloudy", 3: "Overcast",
            45: "Fog", 48: "Rime Fog", 51: "L. Drizzle", 53: "Drizzle",
            55: "H. Drizzle", 56: "Freez Drizzle", 57: "H. Freez Drizzle",
            61: "L. Rain", 63: "Rain", 65: "H. Rain", 66: "Freez Rain",
            67: "H. Freez Rain", 71: "L. Snow", 73: "Snow", 75: "H. Snow",
            77: "Snow Grains", 80: "L. Showers", 81: "Showers", 82: "H. Showers",
            85: "L. Snow Shwrs", 86: "Snow Shwrs", 95: "Thunderstorms",
            96: "T-Storm/Hail", 99: "H. T-Storm/Hail"
        }
        return wmo_codes.get(code, "Unknown")
