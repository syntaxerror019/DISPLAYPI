import requests
import json

LAT = 42.4184
LON = -71.1062

w_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m&wind_speed_unit=mph&timezone=auto"
w_resp = requests.get(w_url)
print("Weather:", w_resp.status_code)
if w_resp.status_code != 200:
    print(w_resp.text)

p_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen&timezone=auto"
p_resp = requests.get(p_url)
print("Pollen:", p_resp.status_code)
if p_resp.status_code != 200:
    print(p_resp.text)
