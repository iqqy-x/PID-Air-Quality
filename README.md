# Air Quality & ISPA Analysis Pipeline

## Overview
An automated ETL pipeline that collects real-time air quality data from WeatherAPI, processes it through PostgreSQL, and correlates pollution metrics with ISPA (Acute Respiratory Infection) prevalence across Indonesian cities.

## Architecture
```
┌──────────────┐
│  WeatherAPI  │ (Current weather + air quality)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Ingest    │ → data/raw/*.json
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│ raw_air_quality
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Transform   │
│    & Clean   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│clean_air_quality
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Daily     │
│ Aggregation  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│daily_air_quality
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Join ISPA   │ ← ispa_province (seeded data)
│     Data     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│city_ispa_joined (Final analysis table)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Streamlit  │
│  Dashboard   │
└──────────────┘
```

## Features
- Real-time air quality monitoring for 10 major Indonesian cities
- Automated ETL pipeline with incremental data processing
- Daily pollution metrics aggregation (PM2.5, PM10, AQI, O3, NO2, SO2, CO)
- ISPA prevalence correlation analysis by province
- Interactive Streamlit dashboard with geospatial visualization

## Prerequisites
- Python 3.9+
- Docker & Docker Compose
- WeatherAPI key ([Get it here](https://www.weatherapi.com/))

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
WEATHER_API_KEY=your_weatherapi_key_here
POSTGRES_USER=airquality_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=air_quality_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin_password
```

### 3. Start Docker Services
```bash
docker-compose up -d
```
This starts:
- PostgreSQL database on port `5432`
- pgAdmin web interface on `http://localhost:5050`

### 4. Initialize Database Schema
```bash
python src/database/init_db.py
```
Creates tables:
- `raw_air_quality`
- `clean_air_quality`
- `daily_air_quality`
- `ispa_province`
- `city_ispa_joined`

### 5. Seed ISPA Reference Data
```bash
python src/database/seed_ispa.py
```
Populates `ispa_province` with 2023 prevalence data for 38 Indonesian provinces.

## Usage

### Run Complete ETL Pipeline
```bash
python src/main.py
```

**Pipeline Steps:**
1. **Ingest** - Fetch data from WeatherAPI → `data/raw/*.json`
2. **Insert** - Load raw JSON → `raw_air_quality` table
3. **Transform** - Clean & normalize → `clean_air_quality` table
4. **Aggregate** - Daily averages per city → `daily_air_quality` table
5. **Join** - Merge with ISPA data → `city_ispa_joined` table

### Run Individual Components
```bash
# Data ingestion only
python src/ingest/weather_ingest.py

# Insert raw data to database
python src/database/insert_data.py

# Clean and transform data
python src/transform/clean_transform.py

# Daily aggregation
python src/transform/daily_batch.py

# Build city-ISPA analysis table
python src/analysis/city_ispa_joined.py
```

### Launch Dashboard
```bash
streamlit run dashboard.py
```
Access at `http://localhost:8501`

**Dashboard Features:**
- PM2.5 vs ISPA prevalence scatter plot
- Interactive map showing pollution distribution across Indonesia
- Province-level grouping and filtering

## Monitored Cities
Jakarta, Surabaya, Bandung, Medan, Semarang, Makassar, Palembang, Bekasi, Depok, Tangerang

## Database Access
- **pgAdmin:** `http://localhost:5050`
- **Direct connection:** `localhost:5432`

## Project Structure
```
case1_air_quality/
├── config/
│   ├── city_to_province.yaml    # City-to-province mapping
│   └── settings.yaml             # API & pipeline configuration
├── data/
│   ├── raw/                      # Raw JSON from API
│   ├── processed/                # Processed data (if any)
│   └── coordinates.csv           # City coordinates for mapping
├── src/
│   ├── ingest/
│   │   └── weather_ingest.py     # Fetch data from WeatherAPI
│   ├── database/
│   │   ├── init_db.py            # Create database schema
│   │   ├── insert_data.py        # Insert raw data
│   │   └── seed_ispa.py          # Seed ISPA reference data
│   ├── transform/
│   │   ├── clean_transform.py    # Data cleaning
│   │   └── daily_batch.py        # Daily aggregation
│   ├── analysis/
│   │   └── city_ispa_joined.py   # Join pollution + ISPA
│   └── main.py                   # Main ETL orchestrator
├── dashboard.py                  # Streamlit visualization
├── docker-compose.yml            # PostgreSQL + pgAdmin
└── requirements.txt              # Python dependencies
```

## Configuration

### Modify Monitored Cities
Edit `config/settings.yaml`:
```yaml
cities:
  - Jakarta
  - YourCity
```

### Adjust Data Collection Interval
In `config/settings.yaml`:
```yaml
interval_minutes: 60  # Change as needed
```

## Data Flow
1. **Raw Data:** API response stored as-is in JSON files and `raw_air_quality` table
2. **Clean Data:** Normalized pollution metrics in `clean_air_quality`
3. **Aggregated Data:** Daily averages per city in `daily_air_quality`
4. **Analysis Data:** Yearly city averages joined with provincial ISPA rates in `city_ispa_joined`

## Data Sources
- **Air Quality Data:** [WeatherAPI](https://www.weatherapi.com/)
- **ISPA Prevalence Data:** [Survei Kesehatan Indonesia (SKI) Dalam Angka 2023](https://drive.google.com/file/d/1rjNDG_f8xG6-Y9wmhJUnXhJ-vUFevVJC/view)