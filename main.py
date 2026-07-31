import time
import datetime
from display_renderer import DisplayRenderer
from data_fetcher import DataFetcher
import config
import random

def get_ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, 'th')

def main():
    print("Starting Kitchen Display (Flashy Mode)...")
    renderer = DisplayRenderer()
    fetcher = DataFetcher()
    
    # Wait a bit for initial data fetch
    print("Fetching initial data...")
    renderer.flash_effect("LOADING...", duration=2.0)

    while True:
        try:
            # 1. Clock and Date (Static Flashy)
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = f"{now.strftime('%b')} {get_ordinal(now.day)}"
            
            # Flash time, then hold, then flash date, then hold
            font = renderer.get_random_font()
            renderer.flash_effect(time_str, duration=1.0, font=font)
            time.sleep(2.0)
            
            font = renderer.get_random_font()
            renderer.flash_effect(date_str, duration=1.0, font=font)
            time.sleep(2.0)
            
            # 2. Weather (Static Flashy)
            weather = fetcher.get_weather()
            temp = weather.get("temp")
            desc = weather.get("desc")
            if temp is not None:
                # Format to fit ~16 chars max on 12 matrices
                weather_str = f"{temp:.0f}F {desc[:9]}"
                font = renderer.get_random_font()
                renderer.flash_effect(weather_str, duration=1.0, font=font)
                time.sleep(3.0)
            
            # 3. News (SCROLLING)
            news = fetcher.get_news()
            if news:
                news_str = "  ***  ".join(news)
                # News uses standard font to remain readable while scrolling
                renderer.scroll_text(f"NEWS: {news_str}")
            
            # 4. Countdowns (Static Flashy)
            for name, dt in config.COUNTDOWNS.items():
                delta = dt - datetime.datetime.now()
                days = delta.days
                if days >= 0:
                    countdown_str = f"{name[:5]}: {days}D"
                    font = renderer.get_random_font()
                    renderer.flash_effect(countdown_str, duration=1.0, font=font)
                    time.sleep(2.0)

        except KeyboardInterrupt:
            print("Exiting...")
            renderer.clear()
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
