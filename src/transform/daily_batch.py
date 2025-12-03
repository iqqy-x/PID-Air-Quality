import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

def run_daily_batch():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT
            DATE(timestamp) AS date,
            city,
            AVG(pm25) AS pm25_avg,
            AVG(pm10) AS pm10_avg,
            AVG(aqi) AS aqi_avg,
            AVG(temperature) AS temp_avg,
            AVG(humidity) AS humidity_avg
        FROM clean_air_quality
        GROUP BY DATE(timestamp), city
        ORDER BY DATE(timestamp), city;
    """)

    results = cur.fetchall()
    print(f"Found {len(results)} daily aggregated rows")

    for row in results:
        date, city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg = row

        cur.execute("""
            SELECT COUNT(*) FROM daily_air_quality
            WHERE date=%s AND city=%s
        """, (date, city))

        exists = cur.fetchone()[0]

        if exists:
            print(f"[SKIP] {city} {date} already exists")
            continue

        cur.execute("""
            INSERT INTO daily_air_quality
            (date, city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (date, city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg))

        print(f"[OK] Inserted daily summary for {city} on {date}")

    conn.commit()
    cur.close()
    conn.close()
    print("Daily batch process complete!")

if __name__ == "__main__":
    run_daily_batch()
