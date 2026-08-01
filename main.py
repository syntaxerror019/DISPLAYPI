import time
import datetime
from display_renderer import DisplayRenderer
from data_fetcher import DataFetcher
import config

def get_ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, 'th')

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
                renderer.display_centered_animated(f"T: {t_f:.0f}F {t_c:.0f}C", font=renderer.font_standard)
                
                # Feels Like
                f_f = weather.get("feels_f")
                f_c = weather.get("feels_c")
                renderer.display_centered_animated(f"FL: {f_f:.0f}F {f_c:.0f}C", font=renderer.font_standard)
                
                # Humidity
                hum = weather.get("humidity")
                renderer.display_centered_animated(f"HUM: {hum:.0f}%", font=renderer.font_standard)
                
                # Wind
                wind = weather.get("wind_mph")
                renderer.display_centered_animated(f"WND: {wind:.0f}mph", font=renderer.font_standard)
                
                # Pollen
                pollen = weather.get("pollen")
                renderer.display_centered_animated(f"POL: {pollen}", font=renderer.font_standard)
                
                # --- Forecast (SCROLLING) ---
                f_desc = weather.get("forecast_desc")
                f_max = weather.get("forecast_max_f")
                f_min = weather.get("forecast_min_f")
                f_pop = weather.get("forecast_pop")
                
                forecast_parts = []
                if f_desc:
                    forecast_parts.append(f"TMRO: {f_desc}")
                if f_max is not None and f_min is not None:
                    forecast_parts.append(f"High: {f_max:.0f}F")
                    forecast_parts.append(f"Low: {f_min:.0f}F")
                if f_pop is not None and f_pop > 10:
                    forecast_parts.append(f"Rain: {f_pop}%")
                
                if forecast_parts:
                    forecast_str = " - ".join(forecast_parts)
                    renderer.scroll_text(forecast_str, font=renderer.font_standard)
            
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
