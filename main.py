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
        subprocess.run(["git", "fetch"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
        if "Your branch is behind" in result.stdout:
            print("New update detected! Pulling from repository...")
            renderer.display_epileptic_countdown("UPDATING...", hold_time=1.0)
            subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True)
            print("Update successful. Restarting script...")
            renderer.clear()
            os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        print(f"Auto-update failed: {e}")

def get_closest_countdown():
    if not os.path.exists("countdowns.json"):
        return None, 0
    try:
        with open("countdowns.json", "r") as f:
            countdowns = json.load(f)
            
        closest_event = None
        closest_delta_sec = float('inf')
        now = datetime.datetime.now()
        
        for event_name, date_str in countdowns.items():
            try:
                event_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                event_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                
            delta = (event_datetime - now).total_seconds()
            
            # Find the closest future event (or event that just happened within the last 60s)
            if -60 <= delta < closest_delta_sec:
                closest_delta_sec = delta
                closest_event = event_name
                
        return closest_event, closest_delta_sec
    except Exception as e:
        print(f"Countdown read error: {e}")
        return None, 0

def main():
    print("Starting Professional Kitchen Display...")
    renderer = DisplayRenderer()
    fetcher = DataFetcher()
    
    print("Fetching initial data...")
    renderer.display_centered("LOADING...")
    time.sleep(3)

    loop_count = 0
    last_update_check = 0
    
    while True:
        loop_count += 1
        try:
            # 0. Check for OTA Updates via Git (Throttled to 60s)
            current_time = time.time()
            if current_time - last_update_check > 60:
                check_for_updates(renderer)
                last_update_check = time.time()
                
            # 0.5 Countdown Lock Mode & Checking
            closest_event, closest_delta_sec = get_closest_countdown()
            
            if closest_event and closest_delta_sec <= 0:
                # Event is happening right now!
                renderer.display_celebration(f"{closest_event.upper()}!", duration=60.0, font=renderer.font_standard)
                continue # Skip everything else and start next loop
                
            elif closest_event and closest_delta_sec < 3600:
                # Less than 1 hour away! Lock mode!
                mins = int(closest_delta_sec // 60)
                secs = int(closest_delta_sec % 60)
                
                if closest_delta_sec < 60:
                    cd_text = f"{secs}s UNTIL {closest_event.upper()}!"
                else:
                    cd_text = f"{mins}m {secs}s UNTIL {closest_event.upper()}!"
                    
                renderer.display_centered(cd_text, font=renderer.font_standard)
                time.sleep(1)
                continue # Skip the rest of the loop!
            
            # 1. Clock and Date (30 seconds with blinking colon)
            clock_start = time.time()
            colon_show = True
            
            while time.time() - clock_start < 30:
                now = datetime.datetime.now()
                month_day = now.strftime("%b %d")
                hour = now.strftime("%I").lstrip("0")
                minute = now.strftime("%M")
                ampm = now.strftime("%p")
                
                prefix = f"{month_day}, {hour}"
                colon = ":"
                suffix = f"{minute} {ampm}"
                
                renderer.display_time_with_blinking_colon(prefix, colon, suffix, font=renderer.font_lcd, colon_show=colon_show)
                time.sleep(0.5)
                colon_show = not colon_show
                
            # 2. Weather & Forecast
            weather = fetcher.get_weather()
            if weather:
                t_f = weather.get("temp_f")
                t_c = weather.get("temp_c")
                renderer.display_centered_animated(f"Temp: {t_f:.0f}F {t_c:.0f}C", font=renderer.font_standard)
                
                f_f = weather.get("feels_f")
                f_c = weather.get("feels_c")
                renderer.display_centered_animated(f"Feels: {f_f:.0f}F {f_c:.0f}C", font=renderer.font_standard)
                
                hum = weather.get("humidity")
                renderer.display_centered_animated(f"Humidity: {hum:.0f}%", font=renderer.font_standard)
                
                wind = weather.get("wind_mph")
                renderer.display_centered_animated(f"Wind: {wind:.0f}mph", font=renderer.font_standard)
                
                pollen = weather.get("pollen")
                renderer.display_centered_animated(f"Allergies: {pollen}", font=renderer.font_standard)
                
                f_desc = weather.get("forecast_desc")
                f_max = weather.get("forecast_max_f")
                f_min = weather.get("forecast_min_f")
                f_pop = weather.get("forecast_pop")
                
                forecast_parts = []
                if f_desc:
                    forecast_str = f"Tomorrow's Weather Forecast: {f_desc.capitalize()}"
                    if f_pop is not None and f_pop > 10:
                        forecast_str += f" with a {f_pop}% chance of rain."
                    if f_max is not None and f_min is not None:
                        forecast_str += f" Highs around {f_max:.0f}F and lows around {f_min:.0f}F."
                    renderer.scroll_text(forecast_str, font=renderer.font_standard)
                    
            # 2.5 History Events (Only once every 5 loops)
            if loop_count % 5 == 0:
                history_events = fetcher.get_history()
                if history_events:
                    hist_str = "  ***  ".join(history_events)
                    renderer.scroll_text(f"THIS DAY IN HISTORY: {hist_str}", font=renderer.font_lcd)

            # 3. Normal Countdowns (> 1 hour)
            if closest_event and closest_delta_sec >= 3600 and (loop_count % 5 == 0):
                if closest_delta_sec > 86400:
                    days = int(closest_delta_sec // 86400)
                    cd_text = f"{days} DAYS UNTIL {closest_event.upper()}!"
                else:
                    hours = int(closest_delta_sec // 3600)
                    mins = int((closest_delta_sec % 3600) // 60)
                    cd_text = f"{hours}h {mins}m UNTIL {closest_event.upper()}!"

                renderer.display_epileptic_countdown(cd_text, hold_time=3.0, font=renderer.font_standard, flash=True)
            
            # 4. News (SCROLLING)
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
