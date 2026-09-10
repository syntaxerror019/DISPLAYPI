"""Countdown and holiday date calculations."""

import calendar
import datetime
import json

from . import config


def get_ordinal(n):
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")
    return f"{n}{suffix}"


def get_dynamic_holiday(name, year):
    """Return the date of a floating holiday, or None if not one."""
    name = name.lower()

    if name == "thanksgiving":
        return _nth_weekday(year, 11, calendar.THURSDAY, 4)
    if name in ("mothers day", "mother's day"):
        return _nth_weekday(year, 5, calendar.SUNDAY, 2)
    if name in ("fathers day", "father's day"):
        return _nth_weekday(year, 6, calendar.SUNDAY, 3)
    if name == "labor day":
        return _nth_weekday(year, 9, calendar.MONDAY, 1)
    if name == "memorial day":
        return _last_weekday(year, 5, calendar.MONDAY)
    return None


def _nth_weekday(year, month, weekday, occurrence):
    occurrences = [week[weekday] for week in calendar.monthcalendar(year, month) if week[weekday] != 0]
    return datetime.datetime(year, month, occurrences[occurrence - 1])


def _last_weekday(year, month, weekday):
    occurrences = [week[weekday] for week in calendar.monthcalendar(year, month) if week[weekday] != 0]
    return datetime.datetime(year, month, occurrences[-1])


def parse_event_date(date_str, now):
    """Parse an event date string into a datetime in the future.

    Accepts dynamic holiday names, recurring MM-DD dates, and absolute
    YYYY-MM-DD dates (optionally with a HH:MM:SS time component).
    """
    date_str = date_str.strip()

    dynamic = get_dynamic_holiday(date_str, now.year)
    if dynamic:
        if dynamic < now:
            dynamic = get_dynamic_holiday(date_str, now.year + 1)
        return dynamic

    date_part, _, time_part = date_str.partition(" ")
    time_of_day = _parse_time(time_part)

    date_components = date_part.split("-")

    if len(date_components) == 2:
        return _parse_recurring_date(date_components, time_of_day, now)

    if len(date_components) == 3:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue

    return None


def _parse_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%H:%M:%S").time()
    except (ValueError, TypeError):
        return datetime.time(0, 0, 0)


def _parse_recurring_date(date_components, time_of_day, now):
    month, day = int(date_components[0]), int(date_components[1])

    try:
        event_dt = datetime.datetime(
            now.year, month, day, time_of_day.hour, time_of_day.minute, time_of_day.second
        )
    except ValueError:
        # Invalid date (e.g. Feb 29 in a non-leap year): fall back to prior day.
        event_dt = datetime.datetime(
            now.year, month, day - 1, time_of_day.hour, time_of_day.minute, time_of_day.second
        )

    if event_dt >= now:
        return event_dt

    next_year = now.year + 1
    if month == 2 and day == 29:
        while not calendar.isleap(next_year):
            next_year += 1
    return datetime.datetime(
        next_year, month, day, time_of_day.hour, time_of_day.minute, time_of_day.second
    )


def get_closest_countdown():
    """Return (event_name, seconds_until) for the nearest upcoming event."""
    if not config.COUNTDOWNS_FILE.exists():
        return None, 0

    try:
        with open(config.COUNTDOWNS_FILE, "r") as f:
            countdowns = json.load(f)
    except Exception as exc:
        print(f"Countdown read error: {exc}")
        return None, 0

    closest_event = None
    closest_delta_sec = float("inf")
    now = datetime.datetime.now()

    for event_name, date_str in countdowns.items():
        event_datetime = parse_event_date(date_str, now)
        if not event_datetime:
            continue

        delta = (event_datetime - now).total_seconds()

        # Pick the closest future event (or one that started within the last 60s).
        if -60 <= delta < closest_delta_sec:
            closest_delta_sec = delta
            closest_event = event_name

    return closest_event, closest_delta_sec