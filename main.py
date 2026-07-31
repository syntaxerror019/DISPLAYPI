import time
import datetime
from display_renderer import DisplayRenderer
from data_fetcher import DataFetcher
import config

def get_ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, 'th')

def main():
    print("Starting Kitchen Display...")
    renderer = DisplayRenderer()
    fetcher = DataFetcher()
    
    # Wait a bit for initial data fetch
    print("Fetching initial data...")
    renderer.scroll_text("Loading...", y_offset=0)
    time.sleep(3)

    while True:
        try:
            # 1. Clock and Date
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = f"{now.strftime('%A, %B')} {get_ordinal(now.day)}"
            renderer.scroll_text(f"TIME: {time_str}  ***  DATE: {date_str}")
            
            # 2. Weather
            weather = fetcher.get_weather()
            temp = weather.get("temp")
            desc = weather.get("desc")
            if temp is not None:
                weather_str = f"WEATHER: {temp:.1f}F, {desc}"
                renderer.scroll_text(weather_str)
            else:
                renderer.scroll_text("WEATHER: Unavailable")
            
            # 3. News
            news = fetcher.get_news()
            if news:
                news_str = "  ***  ".join(news)
                renderer.scroll_text(f"NEWS: {news_str}")
            
            # 4. Countdowns
            for name, dt in config.COUNTDOWNS.items():
                delta = dt - datetime.datetime.now()
                days = delta.days
                if days >= 0:
                    renderer.scroll_text(f"COUNTDOWN to {name}: {days} Days!")

        except KeyboardInterrupt:
            print("Exiting...")
            renderer.clear()
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
