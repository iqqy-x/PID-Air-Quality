import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")


def clean_transform():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM raw_air_quality
        WHERE timestamp NOT IN (
            SELECT timestamp FROM clean_air_quality
        )
        ORDER BY timestamp;
    """)

    rows = cur.fetchall()
    print(f"Found {len(rows)} NEW raw rows to clean")

    for row in rows:
        try:
            cur.execute("""
                INSERT INTO clean_air_quality
                (city, timestamp, pm25, pm10, o3, no2, so2, co, aqi, temperature, humidity)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """, (
                row["city"],
                row["timestamp"],
                row["pm25"],
                row["pm10"],
                row["o3"],
                row["no2"],
                row["so2"],
                row["co"],
                row["us_epa_index"],
                row["temperature"],
                row["humidity"],
            ))
            print(f"[OK] Cleaned {row['city']} at {row['timestamp']}")
        except Exception as e:
            print("Cleaning error:", e)

    conn.commit()
    cur.close()
    conn.close()
    print("Clean transform complete!")


if __name__ == "__main__":
    clean_transform()
