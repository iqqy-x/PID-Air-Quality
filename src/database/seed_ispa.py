import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

data = [
    ("Aceh", 1.4),
    ("Sumatera Utara", 0.5),
    ("Sumatera Barat", 1.8),
    ("Riau", 0.8),
    ("Jambi", 0.9),
    ("Sumatera Selatan", 1.7),
    ("Bengkulu", 1.9),
    ("Lampung", 1.9),
    ("Bangka Belitung", 0.6),
    ("Kepulauan Riau", 1.0),
    ("DKI Jakarta", 2.6),
    ("Jawa Barat", 2.2),
    ("Jawa Tengah", 2.5),
    ("DI Yogyakarta", 0.9),
    ("Jawa Timur", 3.2),
    ("Banten", 3.6),
    ("Bali", 2.1),
    ("Nusa Tenggara Barat", 1.9),
    ("Nusa Tenggara Timur", 3.1),
    ("Kalimantan Barat", 1.0),
    ("Kalimantan Tengah", 1.3),
    ("Kalimantan Selatan", 0.7),
    ("Kalimantan Timur", 1.3),
    ("Kalimantan Utara", 1.0),
    ("Sulawesi Utara", 1.3),
    ("Sulawesi Tengah", 0.9),
    ("Sulawesi Selatan", 0.4),
    ("Sulawesi Tenggara", 0.6),
    ("Gorontalo", 0.5),
    ("Sulawesi Barat", 0.4),
    ("Maluku", 1.0),
    ("Maluku Utara", 1.2),
    ("Papua Barat", 2.3),
    ("Papua Barat Daya", 2.7),
    ("Papua", 4.9),
    ("Papua Selatan", 3.6),
    ("Papua Tengah", 18.8),
    ("Papua Pegunungan", 10.7),
]

def seed():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute("DELETE FROM ispa_province;")

    cur.executemany(
        "INSERT INTO ispa_province (province, prevalence_2023) VALUES (%s, %s);",
        data
    )

    conn.commit()
    cur.close()
    conn.close()
    print("ISPA province data seeded successfully!")

if __name__ == "__main__":
    seed()
