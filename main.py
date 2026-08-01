import time
import datetime
from display_renderer import DisplayRenderer
from data_fetcher import DataFetcher
import config
import json
import os
import sys
import subprocess

def get_ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, 'th')

def check_for_updates(renderer):
    try:
        # Fetch latest changes from remote
        subprocess.run(["git", "fetch"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if we are behind origin/main
        result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
        if "Your branch is behind" in result.stdout:
            print("New update detected! Pulling from repository...")
            renderer.display_epileptic_countdown("UPDATING...", hold_time=1.0)
            
            # Autostash will save local countdowns.json, pull, and re-apply
            subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True)
            print("Update successful. Restarting script...")
            
            # Clear the display before restart so it isn't frozen
            renderer.clear()
            
            # Completely replace the current process with the new version of itself
            os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        print(f"Auto-update failed: {e}")

def main():
    print("Starting Professional Kitchen Display...")
    renderer = DisplayRenderer()
    fetcher = DataFetcher()
    
    # Wait a bit for initial data fetch
    print("Fetching initial data...")
    renderer.display_centered("LOADING...")
    time.sleep(3)

    while True:
        try:
            # 0. Check for OTA Updates via Git
            check_for_updates(renderer)
            
            # 1. Clock and Date (30 seconds with blinking colon)
            clock_start = time.time()
            colon_show = True
            
            while time.time() - clock_start < 30:
                now = datetime.datetime.now()
                # Format: "Jul 31 5:26 PM" or "Jul 31 5 26 PM" based on colon_show
                month_day = now.strftime("%b %d")
                hour = now.strftime("%I").lstrip("0") # Remove leading zero
                minute = now.strftime("%M")
                ampm = now.strftime("%p")
                
                prefix = f"{month_day} {hour}"
                colon = ":"
                suffix = f"{minute} {ampm}"
                
                renderer.display_time_with_blinking_colon(prefix, colon, suffix, font=renderer.font_lcd, colon_show=colon_show)
                
                # Toggle colon every 0.5s
                colon_show = not colon_show
                time.sleep(0.5)
            
            # 2. Weather Data Points (3 seconds each)
            weather = fetcher.get_weather()
            if weather.get("temp_f") is not None:
                # Temp
                t_f = weather.get("temp_f")
                t_c = weather.get("temp_c")
                renderer.display_centered_animated(f"Temp: {t_f:.0f}F {t_c:.0f}C", font=renderer.font_standard)
                
                # Feels Like
                f_f = weather.get("feels_f")
                f_c = weather.get("feels_c")
                renderer.display_centered_animated(f"Feels: {f_f:.0f}F {f_c:.0f}C", font=renderer.font_standard)
                
                # Humidity
                hum = weather.get("humidity")
                renderer.display_centered_animated(f"Humidity: {hum:.0f}%", font=renderer.font_standard)
                
                # Wind
                wind = weather.get("wind_mph")
                renderer.display_centered_animated(f"Wind: {wind:.0f}mph", font=renderer.font_standard)
                
                # Pollen
                pollen = weather.get("pollen")
                renderer.display_centered_animated(f"Pollen: {pollen}", font=renderer.font_standard)
                
                # --- Forecast (SCROLLING) ---
                f_desc = weather.get("forecast_desc")
                f_max = weather.get("forecast_max_f")
                f_min = weather.get("forecast_min_f")
                f_pop = weather.get("forecast_pop")
                
                forecast_parts = []
                if f_desc:
                    forecast_parts.append(f"Tomorrow's Weather Forecast:           {f_desc}")
                if f_max is not None and f_min is not None:
                    forecast_parts.append(f"High Temp: {f_max:.0f}F")
                    forecast_parts.append(f"Low Temp: {f_min:.0f}F")
                if f_pop is not None and f_pop > 10:
                    forecast_parts.append(f"Chance of Rain: {f_pop}%")
                
                if forecast_parts:
                    forecast_str = " - ".join(forecast_parts)
                    renderer.scroll_text(forecast_str, font=renderer.font_standard)
                    
                # --- Countdowns ---
                if os.path.exists("countdowns.json"):
                    try:
                        with open("countdowns.json", "r") as f:
                            countdowns = json.load(f)
                            
                        closest_event = None
                        closest_days = float('inf')
                        today = datetime.date.today()
                        
                        for event_name, date_str in countdowns.items():
                            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                            delta = (event_date - today).days
                            
                            # Find the closest future event
                            if 0 <= delta < closest_days:
                                closest_days = delta
                                closest_event = event_name
                                
                        if closest_event:
                            cd_text = f"{closest_days} DAYS UNTIL {closest_event.upper()}!"
                            renderer.display_epileptic_countdown(cd_text, hold_time=3.0, font=renderer.font_standard)
                    except Exception as e:
                        print(f"Countdown error: {e}")
            
            # 3. News (SCROLLING)
            news = fetcher.get_news()
            if news:
                news_str = "  ***  ".join(news)
                renderer.scroll_text(f"NEWS: {news_str}", font=renderer.font_lcd)

        except KeyboardInterrupt:
            print("Exiting...")
            renderer.clear()
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
