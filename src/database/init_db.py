import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

def create_tables():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    # Raw Data Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_air_quality (
            id SERIAL PRIMARY KEY,
            city VARCHAR(50),
            timestamp TIMESTAMP,
            temperature FLOAT,
            humidity FLOAT,
            wind_speed FLOAT,
            pm25 FLOAT,
            pm10 FLOAT,
            o3 FLOAT,
            no2 FLOAT,
            so2 FLOAT,
            co FLOAT,
            us_epa_index INT,
            raw_json JSONB
        );
    """)

    # Clean Data Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clean_air_quality (
            id SERIAL PRIMARY KEY,
            city VARCHAR(50),
            timestamp TIMESTAMP,
            pm25 FLOAT,
            pm10 FLOAT,
            o3 FLOAT,
            no2 FLOAT,
            so2 FLOAT,
            co FLOAT,
            aqi FLOAT,
            temperature FLOAT,
            humidity FLOAT
        );
    """)

    # Daily Aggregation Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_air_quality (
            id SERIAL PRIMARY KEY,
            date DATE,
            city VARCHAR(50),
            pm25_avg FLOAT,
            pm10_avg FLOAT,
            aqi_avg FLOAT,
            temp_avg FLOAT,
            humidity_avg FLOAT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()
