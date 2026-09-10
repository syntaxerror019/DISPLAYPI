"""Main application loop that drives the LED display."""

import time
import datetime

from . import config
from .countdown import get_closest_countdown
from .data_fetcher import DataFetcher
from .display_renderer import DisplayRenderer
from .updater import check_for_updates


class App:
    """Orchestrates the infinite display loop for the LED matrix."""

    CLOCK_DURATION_SECONDS = 30
    HISTORY_EVERY_N_LOOPS = 5
    COUNTDOWN_EVERY_N_LOOPS = 5
    COUNTDOWN_LOCK_WINDOW_SECONDS = 3600  # < 1 hour: lock the display
    NEWS_SEPARATOR = "  ***  "

    def __init__(self):
        self.renderer = DisplayRenderer()
        self.fetcher = DataFetcher()

    def run(self):
        print("Starting Professional Kitchen Display...")
        print("Fetching initial data...")
        self.renderer.display_centered("LOADING...")
        time.sleep(3)

        loop_count = 0
        last_update_check = 0.0

        while True:
            loop_count += 1
            try:
                current_time = time.time()
                if current_time - last_update_check > config.UPDATE_CHECK_INTERVAL:
                    check_for_updates(self.renderer)
                    last_update_check = current_time

                closest_event, closest_delta_sec = get_closest_countdown()

                if self._run_countdown_lock_mode(closest_event, closest_delta_sec):
                    continue

                self._run_clock()

                self._run_weather()
                self._run_history(loop_count)
                self._run_countdown(loop_count, closest_event, closest_delta_sec)
                self._run_news()

            except KeyboardInterrupt:
                print("Exiting...")
                self.renderer.clear()
                break
            except Exception as exc:
                print(f"Main loop error: {exc}")
                time.sleep(5)

    def _run_countdown_lock_mode(self, closest_event, closest_delta_sec):
        """Lock the display on a live countdown when an event is imminent."""
        if closest_event and closest_delta_sec <= 0:
            self.renderer.display_celebration(
                f"{closest_event.upper()}!", duration=60.0, font=self.renderer.font_standard
            )
            return True

        if closest_event and closest_delta_sec < config.COUNTDOWN_LOCK_WINDOW_SECONDS:
            mins = int(closest_delta_sec // 60)
            secs = int(closest_delta_sec % 60)

            if closest_delta_sec < 60:
                countdown_text = f"{secs}s UNTIL {closest_event.upper()}!"
            else:
                countdown_text = f"{mins}m {secs}s UNTIL {closest_event.upper()}!"

            self.renderer.display_centered(countdown_text, font=self.renderer.font_standard)
            time.sleep(1)
            return True

        return False

    def _run_clock(self):
        start_time = time.time()
        colon_show = True

        while time.time() - start_time < self.CLOCK_DURATION_SECONDS:
            now = datetime.datetime.now()
            month_day = now.strftime("%b %d")
            hour = now.strftime("%I").lstrip("0")
            minute = now.strftime("%M")
            ampm = now.strftime("%p")

            prefix = f"{month_day}, {hour}"
            suffix = f"{minute} {ampm}"

            self.renderer.display_time_with_blinking_colon(
                prefix,
                ":",
                suffix,
                font=self.renderer.font_lcd,
                colon_show=colon_show,
            )
            time.sleep(0.5)
            colon_show = not colon_show

    def _run_weather(self):
        weather = self.fetcher.get_weather()
        if not weather or weather.get("temp_c") is None:
            return

        self._show_animated(f"Temp: {weather['temp_f']:.0f}F {weather['temp_c']:.0f}C")
        self._show_animated(f"Feels: {weather['feels_f']:.0f}F {weather['feels_c']:.0f}C")
        self._show_animated(f"Humidity: {weather['humidity']:.0f}%")
        self._show_animated(f"Wind: {weather['wind_mph']:.0f}mph")
        self._show_animated(f"Allergies: {weather['pollen']}")

        forecast = self._format_forecast(weather)
        if forecast:
            self.renderer.scroll_text(forecast, font=self.renderer.font_standard)

    def _format_forecast(self, weather):
        description = weather.get("forecast_desc")
        if not description:
            return None

        forecast = f"Tomorrow's Weather Forecast: {description.capitalize()}"

        pop = weather.get("forecast_pop")
        if pop is not None and pop > 10:
            forecast += f" with a {pop}% chance of rain."

        forecast_max_f = weather.get("forecast_max_f")
        forecast_min_f = weather.get("forecast_min_f")
        forecast_max_c = weather.get("forecast_max_c")
        forecast_min_c = weather.get("forecast_min_c")
        if None not in (forecast_max_f, forecast_min_f, forecast_max_c, forecast_min_c):
            forecast += (
                f" Highs around {forecast_max_f:.0f}F ({forecast_max_c:.0f}C)"
                f" and lows around {forecast_min_f:.0f}F ({forecast_min_c:.0f}C)."
            )

        return forecast

    def _run_history(self, loop_count):
        if loop_count % self.HISTORY_EVERY_N_LOOPS != 0:
            return

        history_events = self.fetcher.get_history()
        if history_events:
            first_event = history_events[0]
            self.renderer.scroll_text(
                f"On This Day in History...  {first_event}", font=self.renderer.font_lcd
            )

    def _run_countdown(self, loop_count, closest_event, closest_delta_sec):
        if not closest_event or closest_delta_sec < config.COUNTDOWN_LOCK_WINDOW_SECONDS:
            return

        if loop_count % self.COUNTDOWN_EVERY_N_LOOPS != 0:
            return

        if closest_delta_sec > 86400:
            days = int(closest_delta_sec // 86400)
            countdown_text = f"{days} DAYS UNTIL {closest_event.upper()}!"
        else:
            hours = int(closest_delta_sec // 3600)
            mins = int((closest_delta_sec % 3600) // 60)
            countdown_text = f"{hours}h {mins}m UNTIL {closest_event.upper()}!"

        self.renderer.display_epileptic_countdown(
            countdown_text, hold_time=3.0, font=self.renderer.font_standard, flash=True
        )

    def _run_news(self):
        news = self.fetcher.get_news()
        if news:
            news_str = self.NEWS_SEPARATOR.join(news)
            self.renderer.scroll_text(
                f"Latest World News: {news_str}", font=self.renderer.font_lcd
            )

    def _show_animated(self, text):
        self.renderer.display_centered_animated(text, font=self.renderer.font_standard)