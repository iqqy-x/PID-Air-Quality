import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import yaml

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

CITIES = config["cities"]
BASE_URL = config["weather_api"]["base_url"]
AQI = config["weather_api"]["aqi"]
RAW_PATH = config["paths"]["raw_data"]

os.makedirs(RAW_PATH, exist_ok=True)

def fetch_city_weather(city):
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": AQI
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()

def save_raw(data, city):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RAW_PATH}/{city}_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"[OK] Saved raw data: {filename}")

def run_ingest():
    print("Running WeatherAPI ingest...")

    for city in CITIES:
        print(f"Fetching data for: {city}")
        data = fetch_city_weather(city)
        save_raw(data, city)

    print("Ingest completed!")

if __name__ == "__main__":
    run_ingest()
