import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

# --- KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Dashboard ISPA & Polusi")

# --- KONEKSI DATABASE ---
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

def load_city_ispa():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    query = "SELECT * FROM city_ispa_joined ORDER BY city;"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Gabungkan dengan data koordinat
    coords = pd.read_csv('coordinates.csv')
    df = df.merge(coords, on='city', how='left')
    
    return df

# --- MAIN APP ---
st.title("📊 Air Quality & ISPA Dashboard")

# Load Data
try:
    df = load_city_ispa()
except Exception as e:
    st.error(f"Gagal memuat database: {e}")
    st.stop()

# Layout 2 Kolom (Kiri: Scatter, Kanan: Peta)
col1, col2 = st.columns(2)

# 1. SCATTER PLOT (YANG ANDA INGINKAN)
with col1:
    st.subheader("📈 Korelasi: PM2.5 vs ISPA")
    fig_scatter = px.scatter(
        df,
        x="pm25_yearly",
        y="prevalence_2023",
        color="province",
        hover_name="city",
        size="pm25_yearly",
        title="PM2.5 vs ISPA 2023 (Per Kota)",
        template="plotly_dark" # Opsional: tema gelap agar sesuai screenshot
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# 2. PETA GEOSPASIAL (BARU)
with col2:
    st.subheader("🗺️ Peta Sebaran Polusi")
    
    # Cek apakah kolom latitude/longitude ada
    if 'latitude' in df.columns and 'longitude' in df.columns:
        fig_map = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            color="pm25_yearly",      # Warna berdasarkan PM2.5
            color_continuous_scale="RdYlGn_r",  # Merah-Kuning-Hijau (reversed: tinggi=merah, rendah=hijau)
            size="pm25_yearly",       # Ukuran bulatan berdasarkan tingkat polusi
            hover_name="city",
            hover_data={"prevalence_2023": True, "pm25_yearly": True, "province": True},
            zoom=4,                   # Level zoom awal (fokus Indonesia)
            center={"lat": -2.5, "lon": 118}, # Tengah peta Indonesia
            mapbox_style="carto-positron", # Style peta gratis (tidak butuh token API)
            title="Peta Sebaran PM2.5 per Kota"
        )
        # Jika ingin tema gelap pada peta juga, ganti mapbox_style="carto-darkmatter"
        
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("⚠️ Data tidak memiliki kolom 'latitude' dan 'longitude'. Peta tidak dapat ditampilkan.")
        st.info("Saran: Tambahkan kolom koordinat ke database Anda atau gabungkan dengan file CSV koordinat kota di Python.")