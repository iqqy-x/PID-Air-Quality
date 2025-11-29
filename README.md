# Air Quality Monitoring Pipeline

## Overview
Automated ETL pipeline for collecting, processing, and analyzing air quality data from multiple Indonesian cities.

## Architecture
```
┌─────────────┐
│ WeatherAPI  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Ingest    │ → data/raw/*.json
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PostgreSQL │
│   (Raw)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Transform  │
│  & Clean    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Daily     │
│ Aggregation │
└─────────────┘
```

## Setup

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- WeatherAPI key

### Installation

1. Clone repository:
```bash
git clone <repo-url>
cd case1_air_quality
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Start PostgreSQL:
```bash
docker-compose up -d
```

6. Initialize database:
```bash
python -m src.database.init_db
```

## Usage

### Run Full Pipeline
```bash
python -m src.main
```

### Run Individual Components
```bash
# Ingest only
python -m src.ingest.weather_ingest

# Insert raw data
python -m src.database.insert_data

# Transform data
python -m src.transform.clean_transform

# Daily aggregation
python -m src.transform.daily_batch
```

## Testing
```bash
python -m pytest tests/
```

## Project Structure
See [STRUCTURE.md](docs/STRUCTURE.md)

## License
MIT