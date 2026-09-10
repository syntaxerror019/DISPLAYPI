"""MBTA bus arrival predictions for the weekday morning commute."""

import datetime

import requests

from . import config


def is_in_bus_window(date=None):
    """Return True on weekdays between the configured morning bus window."""
    if date is None:
        date = datetime.datetime.now()

    if date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False

    start = datetime.datetime.strptime(config.MBTA_WINDOW_START, "%H:%M").time()
    end = datetime.datetime.strptime(config.MBTA_WINDOW_END, "%H:%M").time()
    return start <= date.time() < end


def get_bus_predictions():
    """Return minutes until arrival for the next buses at the configured stop.

    Predictions are ordered soonest-first and trimmed to MBTA_MAX_BUSES.
    """
    params = {
        "filter[stop]": str(config.MBTA_STOP_ID),
        "filter[route]": str(config.MBTA_ROUTE_ID),
        "api_key": config.MBTA_API_KEY,
    }
    resp = requests.get(config.MBTA_PREDICTIONS_URL, params=params, timeout=10)
    resp.raise_for_status()

    now = datetime.datetime.now(datetime.timezone.utc)
    arrivals = []

    for prediction in resp.json().get("data", []):
        arrival_time = prediction.get("attributes", {}).get("arrival_time")
        if arrival_time is None:
            continue

        arrival = datetime.datetime.fromisoformat(
            arrival_time[:-1] + "+00:00" if arrival_time.endswith("Z") else arrival_time
        )
        minutes = int((arrival - now).total_seconds() // 60)
        arrivals.append((arrival, max(0, minutes)))

    arrivals.sort(key=lambda item: item[0])
    return [minutes for _arrival, minutes in arrivals[: config.MBTA_MAX_BUSES]]


def format_bus_message(predictions):
    """Build the on-screen message from a list of minute counts."""
    return ", ".join(f"Bus {i + 1}: {minutes} mins" for i, minutes in enumerate(predictions))