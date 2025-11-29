import os
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
import yaml

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

RAW_PATH = config["paths"]["raw_data"]

def insert_raw_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    for file_name in os.listdir(RAW_PATH):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(RAW_PATH, file_name)

        cur.execute("SELECT COUNT(*) FROM raw_air_quality WHERE file_name=%s", (file_name,))
        already = cur.fetchone()[0]

        if already:
            print(f"[SKIP] {file_name} already inserted")
            continue

        with open(file_path, "r") as f:
            data = json.load(f)

        city = data["location"]["name"]
        timestamp = datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M")

        current = data["current"]
        air = current["air_quality"]

        cur.execute("""
            INSERT INTO raw_air_quality
            (city, timestamp, temperature, humidity, wind_speed,
             pm25, pm10, o3, no2, so2, co, us_epa_index, raw_json, file_name)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            city, timestamp, current["temp_c"], current["humidity"], current["wind_kph"],
            air.get("pm2_5"), air.get("pm10"), air.get("o3"),
            air.get("no2"), air.get("so2"), air.get("co"),
            air.get("us-epa-index"),
            json.dumps(data),
            file_name
        ))

        print(f"[OK] Inserted {file_name}")

    conn.commit()
    cur.close()
    conn.close()
    print("All raw data inserted.")

if __name__ == "__main__":
    insert_raw_data()
