# 📁 Project Structure Documentation

## Directory Layout

```
PID-Air-Quality/
├── 📁 src/                              # Source code
│   ├── __init__.py
│   ├── main.py                          # Pipeline orchestrator (entry point)
│   │
│   ├── 📁 ingest/                       # Data collection
│   │   ├── __init__.py
│   │   └── weather_ingest.py            # WeatherAPI data fetcher
│   │
│   ├── 📁 database/                     # Database layer
│   │   ├── __init__.py
│   │   ├── init_db.py                   # Schema creation
│   │   └── insert_data.py               # Raw data persistence
│   │
│   ├── 📁 transform/                    # Data transformation
│   │   ├── __init__.py
│   │   ├── clean_transform.py           # Data cleaning & validation
│   │   └── daily_batch.py               # Daily aggregation
│   │
│   ├── 📁 analysis/                     # Analysis & insights
│   │   ├── __init__.py
│   │   └── city_ispa_joined.py          # City-ISPA join
│   │
│   └── 📁 utils/                        # Shared utilities
│       ├── __init__.py
│       ├── db_connection.py             # Database utilities
│       ├── config.py                    # Config management
│       └── logger.py                    # Logging setup
│
├── 📁 config/                           # Configuration files
│   ├── settings.yaml                    # Main configuration
│   └── city_to_province.yaml            # City-province mapping
│
├── 📁 data/                             # Data directory (generated)
│   ├── raw/                             # Raw API responses
│   ├── processed/                       # Processed data
│   └── logs/                            # Application logs
│
├── 📁 tests/                            # Test suite
│   ├── __init__.py
│   ├── test_database.py                 # Database tests
│   ├── test_config.py                   # Config tests
│   └── test_ingest.py                   # Ingest tests
│
├── 📁 .github/                          # GitHub configuration
│   └── workflows/
│       └── tests.yml                    # CI/CD workflow
│
├── dashboard.py                         # Streamlit dashboard
├── Dockerfile                           # Container image
├── docker-compose.yml                   # Docker services
├── Makefile                             # Development commands
├── requirements.txt                     # Python dependencies
├── pytest.ini                           # Pytest configuration
├── setup.cfg                            # Tool configuration
├── .env.example                         # Environment template
├── .gitignore                           # Git ignore rules
└── README.md                            # Documentation
```

## Module Descriptions

### `src/ingest/`

**Purpose**: Fetch external data from APIs

- **`weather_ingest.py`**
  - Class: `WeatherIngestor`
  - Methods:
    - `fetch_city_weather(city)` - Fetch from WeatherAPI
    - `save_raw_data(data, city)` - Save JSON files
    - `run()` - Main orchestration
  - Output: JSON files in `data/raw/`

### `src/database/`

**Purpose**: Database initialization and data persistence

- **`init_db.py`**
  - Creates database tables
  - Sets up indexes for performance
  - Defines schema constraints
  
- **`insert_data.py`**
  - Class: `RawDataInserter`
  - Reads raw JSON files
  - Validates data structure
  - Inserts into `raw_air_quality` table
  - Handles duplicates

### `src/transform/`

**Purpose**: Data cleaning and aggregation

- **`clean_transform.py`**
  - Class: `DataCleaner`
  - Selects new raw records
  - Validates and cleans data
  - Inserts into `clean_air_quality` table
  
- **`daily_batch.py`**
  - Class: `DailyAggregator`
  - Calculates daily averages
  - Groups by city and date
  - Inserts into `daily_air_quality` table

### `src/analysis/`

**Purpose**: Business logic and insights

- **`city_ispa_joined.py`**
  - Class: `CityISPAJoiner`
  - Aggregates yearly metrics
  - Joins with ISPA province data
  - Final analytical table

### `src/utils/`

**Purpose**: Shared utilities

- **`db_connection.py`**
  - `get_db_connection()` - Connection pool
  - `execute_query()` - Safe query execution
  - `execute_batch_insert()` - Batch operations
  
- **`config.py`**
  - `load_config()` - Load YAML config
  - `load_city_mapping()` - City-province map
  - `get_db_credentials()` - Env variables
  
- **`logger.py`**
  - `get_logger()` - Configured logger
  - File and console handlers

## Data Flow Diagram

```
WeatherAPI
    ↓
weather_ingest.py (ingest/)
    ↓ (raw JSON files)
insert_data.py (database/)
    ↓
raw_air_quality table
    ↓
clean_transform.py (transform/)
    ↓
clean_air_quality table
    ↓
daily_batch.py (transform/)
    ↓
daily_air_quality table
    ↓
city_ispa_joined.py (analysis/)
    ↓
city_ispa_joined table (FINAL)
    ↓
dashboard.py (visualization/)
    ↓
Streamlit UI
```

## Configuration Files

### `config/settings.yaml`

```yaml
cities:           # List of cities to monitor
weather_api:      # WeatherAPI settings
  base_url: ...   # API endpoint
  aqi: ...        # Include AQI data

paths:
  raw_data: ...   # Where to save raw JSON
  logs: ...       # Log directory
```

### `config/city_to_province.yaml`

```yaml
City1: Province1
City2: Province2
```

Maps each city to its province for ISPA aggregation.

## Key Classes & Patterns

### Orchestrator Pattern

```python
# src/main.py
class DataPipeline:
    def __init__(self):
        self.steps = [
            PipelineStep("INGEST", run_ingest, ...),
            PipelineStep("INSERT", insert_raw_data, ...),
            # ... more steps
        ]
    
    def run(self):
        for step in self.steps:
            step.execute()
```

### Manager Pattern

```python
# src/dashboard.py
class DashboardData:
    @st.cache_data(ttl=3600)
    def load_city_ispa(self):
        # Database query with caching
```

### Configuration Manager

```python
# src/utils/config.py
class ConfigManager:
    load_config()        # YAML configuration
    load_city_mapping()  # City mappings
    get_db_credentials() # Environment variables
```

## Database Schema

### Tables

1. **raw_air_quality** - Raw API responses
2. **clean_air_quality** - Cleaned data
3. **daily_air_quality** - Daily aggregates
4. **ispa_province** - ISPA reference data
5. **city_ispa_joined** - Final analytical table

### Relationships

```
ispa_province
    ↓ (province)
city_ispa_joined ← daily_air_quality
                ↓ (city)
            clean_air_quality
                ↓ (timestamp)
            raw_air_quality
```

## Development Workflow

### Adding a New Module

1. Create folder in `src/`
2. Add `__init__.py`
3. Implement main class
4. Add utility functions
5. Create tests in `tests/`
6. Update documentation

### Adding a New Pipeline Step

1. Create class inheriting from base pattern
2. Implement `run()` method
3. Add logging
4. Create `PipelineStep` in `main.py`
5. Test with `pytest`

## Testing Strategy

```
tests/
├── test_database.py       # Database operations
├── test_config.py         # Configuration loading
├── test_ingest.py         # API fetching
└── conftest.py            # Pytest fixtures
```

Each module has corresponding test file with:
- Unit tests
- Integration tests
- Fixtures for mock data

## Logging Strategy

- **DEBUG**: Detailed execution flow
- **INFO**: Process milestones
- **WARNING**: Recoverable issues
- **ERROR**: Critical failures

Logs stored in `data/logs/app_*.log`

## Performance Considerations

1. **Database**: Indexed columns for fast queries
2. **Caching**: Streamlit cache for dashboard
3. **Batch Processing**: Bulk inserts
4. **Connection Pooling**: Reuse connections
5. **Query Limits**: LIMIT clauses for large tables
