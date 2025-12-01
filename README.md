# 🌍 Air Quality Monitoring & ISPA Analysis System

**Sistem pemantauan kualitas udara otomatis dengan analisis ISPA (Indeks Standar Pencemar Udara) untuk kota-kota besar di Indonesia.**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)
[![PostgreSQL 15](https://img.shields.io/badge/PostgreSQL-15-336791)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B)](https://streamlit.io/)

---

## 📋 Daftar Isi

- [Fitur](#fitur)
- [Arsitektur](#arsitektur)
- [Prerequisite](#prerequisite)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Penggunaan](#penggunaan)
- [Struktur Proyek](#struktur-proyek)
- [API & Database](#api--database)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

---

## ✨ Fitur

- **⚡ Pipeline Otomatis**: ETL pipeline yang terintegrasi penuh dari ingest hingga analisis
- **📊 Dashboard Interaktif**: Visualisasi real-time dengan Streamlit dan Plotly
- **🗺️ Peta Geografis**: Tampilan sebaran polusi di peta Indonesia
- **📈 Analisis Tren**: Tracking daily, monthly, dan yearly trends
- **🏥 Integrasi ISPA**: Korelasi data polusi dengan indeks kesehatan masyarakat
- **🔄 Auto Sync**: Sinkronisasi data otomatis setiap jam dari WeatherAPI
- **🐘 PostgreSQL**: Database production-ready dengan proper schema
- **🐳 Docker Support**: Containerized environment untuk deployment mudah
- **📝 Logging Komprehensif**: Debug dan monitoring dengan logging terstruktur
- **✅ Error Handling**: Robust error handling di setiap layer

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                    WeatherAPI (Data Source)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ▼ (1. INGEST)
                           │
        ┌──────────────────────────────────────┐
        │  📥 Raw JSON Files (data/raw/*.json) │
        └──────────────────┬───────────────────┘
                           │
                    ▼ (2. INSERT)
                           │
        ┌─────────────────────────────────────────┐
        │ 🐘 PostgreSQL - raw_air_quality table   │
        └──────────────────┬──────────────────────┘
                           │
                    ▼ (3. TRANSFORM)
                           │
        ┌────────────────────────────────────────────┐
        │ 🐘 PostgreSQL - clean_air_quality table    │
        └──────────────────┬───────────────────────┘
                           │
                    ▼ (4. AGGREGATE)
                           │
        ┌─────────────────────────────────────────────┐
        │ 🐘 PostgreSQL - daily_air_quality table     │
        └──────────────────┬────────────────────────┘
                           │
                    ▼ (5. ANALYZE)
                           │
        ┌──────────────────────────────────────────────────┐
        │ 🐘 PostgreSQL - city_ispa_joined table (Final)   │
        └──────────────────┬───────────────────────────────┘
                           │
                    ▼ (VISUALIZE)
                           │
        ┌──────────────────────────────────────────┐
        │ 📊 Streamlit Dashboard (Interactive UI) │
        └──────────────────────────────────────────┘
```

### Data Flow

1. **INGEST**: Fetch data dari WeatherAPI untuk setiap kota
2. **INSERT**: Simpan raw JSON ke PostgreSQL
3. **TRANSFORM**: Cleaning & validation data
4. **AGGREGATE**: Daily aggregation per kota
5. **ANALYZE**: Join dengan ISPA province data
6. **VISUALIZE**: Dashboard interaktif dengan Streamlit

---

## 📦 Prerequisite

- **Python 3.11+**
- **Docker & Docker Compose** (untuk database)
- **PostgreSQL 15** (jika tidak menggunakan Docker)
- **WeatherAPI Key** ([daftar gratis](https://www.weatherapi.com/))
- **Git** untuk version control

---

## 🚀 Instalasi

### Step 1: Clone Repository

```bash
git clone https://github.com/iqqy-x/PID-Air-Quality.git
cd PID-Air-Quality
```

### Step 2: Setup Python Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktivasi (Linux/Mac)
source venv/bin/activate

# Aktivasi (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Konfigurasi Environment

```bash
# Copy template .env
cp .env.example .env

# Edit .env dengan credentials Anda
nano .env
# atau
code .env  # di VS Code
```

**Required environment variables:**

```env
# PostgreSQL
POSTGRES_USER=airquality_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=air_quality_monitoring
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# WeatherAPI
WEATHER_API_KEY=your_weatherapi_key_here

# Optional
LOG_LEVEL=INFO
```

### Step 5: Start PostgreSQL

```bash
# Menggunakan Docker Compose (recommended)
docker-compose up -d postgres

# Atau: Jika PostgreSQL sudah terinstall locally
# service postgresql start
```

### Step 6: Initialize Database

```bash
python -m src.database.init_db
```

---

## ⚙️ Konfigurasi

### File Konfigurasi

#### `config/settings.yaml`

Konfigurasi utama aplikasi:

```yaml
cities:
  - Jakarta
  - Surabaya
  - Bandung
  # ... tambah kota sesuai kebutuhan

weather_api:
  base_url: "https://api.weatherapi.com/v1/current.json"
  aqi: "yes"

interval_minutes: 60

paths:
  raw_data: "data/raw"
  processed_data: "data/processed"
  logs: "data/logs"
```

#### `config/city_to_province.yaml`

Mapping kota ke provinsi (untuk agregasi ISPA):

```yaml
Jakarta: DKI Jakarta
Surabaya: Jawa Timur
Bandung: Jawa Barat
# ... tambah sesuai kebutuhan
```

---

## 💻 Penggunaan

### 1. Menjalankan Full Pipeline

```bash
# Menjalankan semua tahap dari ingest hingga analisis
python -m src.main
```

Output:

```
============================================================
AIR QUALITY MONITORING PIPELINE
============================================================
Total steps: 5

[1/5] Starting INGEST...
[STEP: INGEST] Ingesting data from WeatherAPI (weather + air quality)
------------------------------------------------------------
...
✓ Ingest completed successfully

[2/5] Starting INSERT...
...

✓ All pipeline steps completed successfully!
============================================================
```

### 2. Menjalankan Komponen Individual

```bash
# Hanya ingest dari WeatherAPI
python -m src.ingest.weather_ingest

# Hanya insert raw data ke database
python -m src.database.insert_data

# Hanya transform/clean data
python -m src.transform.clean_transform

# Hanya daily aggregation
python -m src.transform.daily_batch

# Hanya city-ISPA join
python -m src.analysis.city_ispa_joined
```

### 3. Menjalankan Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboard.py

# Dashboard akan terbuka di: http://localhost:8501
```

### 4. Scheduling Pipeline (Optional)

Menggunakan `cron` (Linux/Mac):

```bash
# Edit crontab
crontab -e

# Tambahkan untuk menjalankan pipeline setiap jam
0 * * * * cd /path/to/PID-Air-Quality && python -m src.main >> data/logs/cron.log 2>&1
```

Menggunakan `Task Scheduler` (Windows):

- Buka Task Scheduler
- Buat task baru dengan script: `python -m src.main`
- Set trigger: Hourly

---

## 📁 Struktur Proyek

```
PID-Air-Quality/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Pipeline orchestrator
│   ├── ingest/
│   │   └── weather_ingest.py        # Fetch dari WeatherAPI
│   ├── database/
│   │   ├── init_db.py               # Database initialization
│   │   └── insert_data.py           # Raw data insertion
│   ├── transform/
│   │   ├── clean_transform.py       # Data cleaning & validation
│   │   └── daily_batch.py           # Daily aggregation
│   ├── analysis/
│   │   └── city_ispa_joined.py      # City-ISPA join analysis
│   └── utils/
│       ├── db_connection.py         # Database utilities
│       ├── config.py                # Config management
│       └── logger.py                # Logging setup
│
├── config/
│   ├── settings.yaml                # Main configuration
│   └── city_to_province.yaml        # City mapping
│
├── dashboard.py                     # Streamlit dashboard
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Application container
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .gitignore
└── README.md

data/
├── raw/                             # Raw API responses (JSON)
├── processed/                       # Processed data
└── logs/                            # Application logs
```

---

## 🗄️ API & Database

### Database Schema

#### `raw_air_quality`
Raw data langsung dari API:

```sql
SELECT * FROM raw_air_quality;
-- id | city | timestamp | temperature | humidity | wind_speed | 
-- pm25 | pm10 | o3 | no2 | so2 | co | us_epa_index | raw_json | file_name
```

#### `clean_air_quality`
Data yang sudah dibersihkan:

```sql
SELECT * FROM clean_air_quality;
-- id | city | timestamp | pm25 | pm10 | o3 | no2 | so2 | co | 
-- aqi | temperature | humidity
```

#### `daily_air_quality`
Agregasi harian per kota:

```sql
SELECT * FROM daily_air_quality;
-- id | date | city | pm25_avg | pm10_avg | aqi_avg | 
-- temp_avg | humidity_avg
```

#### `city_ispa_joined`
Final table dengan ISPA province data:

```sql
SELECT * FROM city_ispa_joined;
-- id | city | province | pm25_yearly | pm10_yearly | aqi_yearly |
-- temp_yearly | humidity_yearly | prevalence_2023
```

### Queries Berguna

```sql
-- Top 10 kota dengan PM2.5 tertinggi
SELECT city, pm25_yearly FROM city_ispa_joined 
ORDER BY pm25_yearly DESC LIMIT 10;

-- Korelasi PM2.5 dengan ISPA
SELECT CORR(pm25_yearly, prevalence_2023) AS correlation 
FROM city_ispa_joined;

-- Data terbaru per kota
SELECT DISTINCT ON (city) city, timestamp, pm25, aqi 
FROM clean_air_quality 
ORDER BY city, timestamp DESC;
```

---

## 🐳 Docker Deployment

### Development

```bash
# Start semua services (postgres + pgAdmin)
docker-compose --profile dev up -d

# Access pgAdmin di http://localhost:5050
# Default: admin@example.com / admin
```

### Production

```bash
# Start hanya PostgreSQL
docker-compose up -d postgres

# Run pipeline
python -m src.main

# Run dashboard
streamlit run dashboard.py
```

### Docker Build & Push

```bash
# Build image
docker build -t air-quality-monitor:latest .

# Run container
docker run -p 8501:8501 \
  --env-file .env \
  --network air_quality_network \
  air-quality-monitor:latest
```

---

## 🧪 Testing

```bash
# Run semua tests
python -m pytest tests/ -v

# Run dengan coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_database.py -v
```

---

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL status
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Verify connection
psql -h localhost -U airquality_user -d air_quality_monitoring
```

### WeatherAPI Key Invalid

```bash
# Test API key
curl "https://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=Jakarta&aqi=yes"

# Get new key: https://www.weatherapi.com/
```

### Dashboard Won't Load

```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache

# Run with verbose logging
streamlit run dashboard.py --logger.level=debug

# Check if database is populated
python -c "
from src.utils.db_connection import *
from src.utils.config import get_db_credentials
conn = get_db_connection(**get_db_credentials())
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM city_ispa_joined')
print(cur.fetchone())
"
```

### Pipeline Stuck

```bash
# Check logs
tail -f data/logs/app_*.log

# Kill hung process
pkill -f "python -m src.main"

# Clear locks
python -c "
from src.utils.db_connection import *
from src.utils.config import get_db_credentials
conn = get_db_connection(**get_db_credentials())
cur = conn.cursor()
cur.execute('SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = \"active\"')
"
```

---

## 👨‍💻 Development

### Code Style

```bash
# Format code dengan Black
black src/

# Lint dengan Flake8
flake8 src/

# Type checking dengan mypy
mypy src/
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to repository
git push origin feature/new-feature

# Create Pull Request
```

### Adding New Cities

1. Edit `config/settings.yaml`:

```yaml
cities:
  - Jakarta
  - Surabaya
  - Bandung
  - Medan          # ← Tambah di sini
```

2. Edit `config/city_to_province.yaml`:

```yaml
Jakarta: DKI Jakarta
Medan: Sumatera Utara  # ← Tambah di sini
```

3. Run pipeline:

```bash
python -m src.main
```

---

## 📊 Performance Tips

- **Database Indexes**: Sudah ada di init_db.py
- **Query Optimization**: Gunakan LIMIT di queries besar
- **Cache Strategy**: Dashboard menggunakan @st.cache_data
- **Batch Processing**: Pipeline menggunakan batch insert

---

## 📝 Logging

Logs disimpan di `data/logs/`:

```bash
# View logs
tail -f data/logs/app_*.log

# Search logs
grep "ERROR" data/logs/app_*.log

# Analyze performance
grep -E "Ingestion|Insertion|Cleaning|Aggregation" data/logs/app_*.log
```

---

## 📄 License

MIT License - [LICENSE](LICENSE)

---

## 🤝 Contributing

Kontribusi sangat diterima! Silakan:

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Open Pull Request

---

## 📧 Support

Untuk pertanyaan atau issues:

- GitHub Issues: [PID-Air-Quality/issues](https://github.com/iqqy-x/PID-Air-Quality/issues)
- Email: support@example.com

---

**Terakhir diupdate**: December 2024

Made with ❤️ for Indonesian Air Quality Monitoring
