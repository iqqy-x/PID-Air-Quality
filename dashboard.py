"""
Streamlit Dashboard for Air Quality Monitoring and ISPA Analysis.

This dashboard provides interactive visualizations of air quality metrics
and ISPA (Indonesian Health Index) data across Indonesian cities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Tuple
import os
from dotenv import load_dotenv

from src.utils.db_connection import get_db_connection, close_db_connection, DatabaseConnectionError
from src.utils.config import get_db_credentials, ConfigError
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Dashboard ISPA & Polusi Indonesia",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; color: #1f77b4; margin-bottom: 1rem; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 1rem; border-radius: 0.5rem; }
        .warning-box { background: #fff3cd; color: #856404; padding: 1rem; 
                      border-radius: 0.5rem; border-left: 4px solid #ffc107; }
    </style>
""", unsafe_allow_html=True)


class DashboardData:
    """Handles data loading from database."""
    
    def __init__(self):
        """Initialize dashboard data manager."""
        try:
            self.db_creds = get_db_credentials()
            logger.info("DashboardData initialized")
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
    
    @st.cache_data(ttl=3600)
    def load_city_ispa(self) -> Optional[pd.DataFrame]:
        """
        Load city ISPA joined data from database with caching.
        
        Returns:
            DataFrame with city air quality and ISPA data, or None if failed
        """
        conn = None
        try:
            conn = get_db_connection(**self.db_creds)
            query = "SELECT * FROM city_ispa_joined ORDER BY city;"
            df = pd.read_sql(query, conn)
            
            if df.empty:
                logger.warning("No data found in city_ispa_joined table")
                return None
            
            # Try to merge with coordinates
            try:
                coords = pd.read_csv('coordinates.csv')
                df = df.merge(coords, on='city', how='left')
                logger.info(f"Loaded {len(df)} cities with coordinates")
            except FileNotFoundError:
                logger.warning("coordinates.csv not found, proceeding without coordinates")
            
            return df
            
        except DatabaseConnectionError as e:
            logger.error(f"Database connection failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    @st.cache_data(ttl=3600)
    def load_daily_trends(self, city: str) -> Optional[pd.DataFrame]:
        """
        Load daily trends for a specific city.
        
        Args:
            city: City name
            
        Returns:
            DataFrame with daily metrics
        """
        conn = None
        try:
            conn = get_db_connection(**self.db_creds)
            query = """
                SELECT date, city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg
                FROM daily_air_quality
                WHERE city = %s
                ORDER BY date DESC
                LIMIT 30;
            """
            df = pd.read_sql(query, conn, params=(city,))
            return df if not df.empty else None
            
        except Exception as e:
            logger.error(f"Error loading daily trends: {e}")
            return None
        finally:
            close_db_connection(conn)


def display_header():
    """Display dashboard header with title and description."""
    st.markdown(
        '<div class="main-header">🌍 Dashboard ISPA & Polusi Indonesia</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
        Pantau kualitas udara dan indeks kesehatan masyarakat Indonesia secara real-time.
        Data diperbarui setiap jam dari berbagai kota besar di Indonesia.
    """)
    st.divider()


def display_metrics(df: pd.DataFrame):
    """Display key metrics in columns."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_pm25 = df['pm25_yearly'].mean()
        st.metric("PM2.5 Rata-rata", f"{avg_pm25:.1f} µg/m³", 
                 help="Partikel halus dengan diameter ≤ 2.5 mikron")
    
    with col2:
        avg_pm10 = df['pm10_yearly'].mean()
        st.metric("PM10 Rata-rata", f"{avg_pm10:.1f} µg/m³",
                 help="Partikel dengan diameter ≤ 10 mikron")
    
    with col3:
        avg_aqi = df['aqi_yearly'].mean()
        st.metric("AQI Rata-rata", f"{avg_aqi:.1f}",
                 help="Air Quality Index (US EPA)")
    
    with col4:
        avg_ispa = df['prevalence_2023'].mean()
        st.metric("ISPA Rata-rata", f"{avg_ispa:.1f}%",
                 help="Indonesian Health Index")


def display_scatter_plot(df: pd.DataFrame):
    """Display PM2.5 vs ISPA scatter plot."""
    st.subheader("📊 Korelasi PM2.5 dengan Prevalence ISPA 2023")
    
    fig = px.scatter(
        df,
        x="pm25_yearly",
        y="prevalence_2023",
        color="province",
        hover_name="city",
        size="pm25_yearly",
        title="PM2.5 vs ISPA Prevalence Per Kota (2023)",
        labels={
            "pm25_yearly": "PM2.5 Tahunan (µg/m³)",
            "prevalence_2023": "ISPA Prevalence (%)"
        },
        template="plotly_dark",
        height=500,
        hover_data={
            "pm25_yearly": ":.2f",
            "prevalence_2023": ":.2f",
            "province": True,
            "city": True
        }
    )
    
    fig.update_layout(hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)


def display_map(df: pd.DataFrame):
    """Display geographical map of pollution."""
    st.subheader("🗺️ Peta Sebaran Polusi PM2.5")
    
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        st.warning("⚠️ Data koordinat tidak tersedia. Silakan tambahkan koordinat ke database.")
        return
    
    # Remove rows with missing coordinates
    df_map = df.dropna(subset=['latitude', 'longitude'])
    
    if df_map.empty:
        st.warning("Tidak ada data koordinat yang valid.")
        return
    
    fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        color="pm25_yearly",
        color_continuous_scale="RdYlGn_r",
        size="pm25_yearly",
        hover_name="city",
        hover_data={
            "latitude": ":.4f",
            "longitude": ":.4f",
            "prevalence_2023": ":.2f",
            "pm25_yearly": ":.2f",
            "province": True,
        },
        zoom=4,
        center={"lat": -2.5, "lon": 118},
        mapbox_style="carto-positron",
        title="Peta Sebaran PM2.5 per Kota Indonesia",
        height=600,
        size_max=50,
    )
    
    fig.update_layout(
        hovermode="closest",
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_city_trends(df_city: pd.DataFrame, city_name: str):
    """Display daily trends for a selected city."""
    st.subheader(f"📈 Tren Harian - {city_name}")
    
    if df_city is None or df_city.empty:
        st.info(f"Belum ada data harian untuk {city_name}")
        return
    
    # Reverse to get chronological order
    df_city = df_city.sort_values('date')
    
    col1, col2 = st.columns(2)
    
    # PM2.5 trend
    with col1:
        fig_pm25 = px.line(
            df_city,
            x='date',
            y='pm25_avg',
            title=f'PM2.5 Trend - {city_name}',
            markers=True,
            template="plotly_dark",
            labels={'pm25_avg': 'PM2.5 (µg/m³)', 'date': 'Tanggal'}
        )
        fig_pm25.update_traces(line=dict(color='#FF6B6B', width=2))
        st.plotly_chart(fig_pm25, use_container_width=True)
    
    # AQI trend
    with col2:
        fig_aqi = px.line(
            df_city,
            x='date',
            y='aqi_avg',
            title=f'AQI Trend - {city_name}',
            markers=True,
            template="plotly_dark",
            labels={'aqi_avg': 'AQI', 'date': 'Tanggal'}
        )
        fig_aqi.update_traces(line=dict(color='#4ECDC4', width=2))
        st.plotly_chart(fig_aqi, use_container_width=True)


def display_city_comparison(df: pd.DataFrame):
    """Display comparison across cities."""
    st.subheader("🏙️ Perbandingan Antar Kota")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top cities by PM2.5
        top_pm25 = df.nlargest(10, 'pm25_yearly')[['city', 'pm25_yearly']].sort_values('pm25_yearly')
        fig_pm25 = px.barh(
            top_pm25,
            x='pm25_yearly',
            y='city',
            title='Top 10 Kota dengan PM2.5 Tertinggi',
            labels={'pm25_yearly': 'PM2.5 (µg/m³)', 'city': 'Kota'},
            template="plotly_dark",
            color='pm25_yearly',
            color_continuous_scale='Reds'
        )
        fig_pm25.update_layout(height=400)
        st.plotly_chart(fig_pm25, use_container_width=True)
    
    with col2:
        # Top cities by ISPA
        top_ispa = df.nlargest(10, 'prevalence_2023')[['city', 'prevalence_2023']].sort_values('prevalence_2023')
        fig_ispa = px.barh(
            top_ispa,
            x='prevalence_2023',
            y='city',
            title='Top 10 Kota dengan ISPA Tertinggi',
            labels={'prevalence_2023': 'ISPA (%)', 'city': 'Kota'},
            template="plotly_dark",
            color='prevalence_2023',
            color_continuous_scale='Blues'
        )
        fig_ispa.update_layout(height=400)
        st.plotly_chart(fig_ispa, use_container_width=True)


def display_data_table(df: pd.DataFrame):
    """Display raw data table."""
    st.subheader("📋 Data Detail")
    
    # Select columns to display
    display_cols = ['city', 'province', 'pm25_yearly', 'pm10_yearly', 
                   'aqi_yearly', 'temp_yearly', 'humidity_yearly', 'prevalence_2023']
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Format for display
    df_display = df[available_cols].copy()
    df_display = df_display.round(2)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400
    )


def main():
    """Main dashboard function."""
    try:
        # Initialize data manager
        data_manager = DashboardData()
        
        # Display header
        display_header()
        
        # Load main data
        df = data_manager.load_city_ispa()
        
        if df is None or df.empty:
            st.error("❌ Gagal memuat data dari database. Pastikan database PostgreSQL sedang berjalan.")
            st.info("Silakan jalankan pipeline ingestion terlebih dahulu: `python src/main.py`")
            return
        
        # Display metrics
        display_metrics(df)
        st.divider()
        
        # Main visualizations
        display_scatter_plot(df)
        st.divider()
        
        display_map(df)
        st.divider()
        
        display_city_comparison(df)
        st.divider()
        
        # City-specific analysis
        st.subheader("🔍 Analisis Kota Spesifik")
        
        selected_city = st.selectbox(
            "Pilih Kota",
            sorted(df['city'].unique()),
            key="city_selector"
        )
        
        if selected_city:
            df_city = data_manager.load_daily_trends(selected_city)
            display_city_trends(df_city, selected_city)
        
        st.divider()
        
        # Data table
        display_data_table(df)
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: gray; font-size: 0.85rem;'>
            Dashboard ISPA & Polusi Indonesia | Data diperbarui secara berkala dari WeatherAPI
            </div>
        """, unsafe_allow_html=True)
        
    except ConfigError as e:
        st.error(f"❌ Kesalahan Konfigurasi: {e}")
        st.info("Pastikan file .env sudah dikonfigurasi dengan benar.")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        st.error(f"❌ Terjadi kesalahan: {e}")


if __name__ == "__main__":
    main()