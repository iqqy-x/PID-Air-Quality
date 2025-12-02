import psycopg2
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

with open("config/city_to_province.yaml", "r") as f:
    CITY_TO_PROV = yaml.safe_load(f)

def build_city_ispa():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute("DELETE FROM city_ispa_joined;")

    cur.execute("""
        SELECT city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg
        FROM daily_air_quality;
    """)
    rows = cur.fetchall()

    city_data = {}

    for city, pm25, pm10, aqi, temp, hum in rows:
        province = CITY_TO_PROV.get(city)

        if not province:
            continue

        if city not in city_data:
            city_data[city] = {
                "province": province,
                "pm25": [],
                "pm10": [],
                "aqi": [],
                "temp": [],
                "hum": []
            }

        city_data[city]["pm25"].append(pm25)
        city_data[city]["pm10"].append(pm10)
        city_data[city]["aqi"].append(aqi)
        city_data[city]["temp"].append(temp)
        city_data[city]["hum"].append(hum)

    for city, metrics in city_data.items():

        pm25_yearly = sum(metrics["pm25"]) / len(metrics["pm25"])
        pm10_yearly = sum(metrics["pm10"]) / len(metrics["pm10"])
        aqi_yearly = sum(metrics["aqi"]) / len(metrics["aqi"])
        temp_yearly = sum(metrics["temp"]) / len(metrics["temp"])
        hum_yearly = sum(metrics["hum"]) / len(metrics["hum"])

        province = metrics["province"]

        cur.execute("""
            SELECT prevalence_2023
            FROM ispa_province
            WHERE province = %s;
        """, (province,))
        ispa = cur.fetchone()

        if not ispa:
            continue

        prevalence_2023 = ispa[0]

        cur.execute("""
            INSERT INTO city_ispa_joined
            (city, province, pm25_yearly, pm10_yearly, aqi_yearly,
             temp_yearly, humidity_yearly, prevalence_2023)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            city, province, pm25_yearly, pm10_yearly, aqi_yearly,
            temp_yearly, hum_yearly, prevalence_2023
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("city_ispa_joined updated.")

if __name__ == "__main__":
    build_city_ispa()
