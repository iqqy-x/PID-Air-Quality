# API Reference & Database Guide

## Table of Contents

1. [Python API](#python-api)
2. [Database Queries](#database-queries)
3. [Configuration API](#configuration-api)
4. [Logging API](#logging-api)

---

## Python API

### Database Connection Module

#### `src.utils.db_connection`

```python
from src.utils.db_connection import (
    get_db_connection,
    close_db_connection,
    execute_query,
    execute_insert,
    DatabaseConnectionError
)

# Get connection
conn = get_db_connection(
    host="localhost",
    database="air_quality_monitoring",
    user="airquality_user",
    password="password",
    port=5432
)

# Execute SELECT
results = execute_query(conn, "SELECT * FROM city_ispa_joined", fetch=True)

# Execute INSERT
success = execute_insert(
    conn,
    "INSERT INTO table (col1, col2) VALUES (%s, %s)",
    ("value1", "value2")
)

# Close safely
close_db_connection(conn)
```

### Configuration Module

#### `src.utils.config`

```python
from src.utils.config import (
    load_config,
    load_city_mapping,
    get_db_credentials,
    ConfigError
)

# Load main configuration
config = load_config("config/settings.yaml")
cities = config["cities"]
api_url = config["weather_api"]["base_url"]

# Load city mapping
mapping = load_city_mapping("config/city_to_province.yaml")
province = mapping.get("Jakarta")

# Get database credentials from .env
db_creds = get_db_credentials()  # Returns dict
```

### Logger Module

#### `src.utils.logger`

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Processing started")
logger.warning("This might be slow")
logger.error("An error occurred")
logger.debug("Debug information")
```

### Ingest Module

#### `src.ingest.weather_ingest`

```python
from src.ingest.weather_ingest import WeatherIngestor

# Initialize
ingestor = WeatherIngestor()  # Uses config + env vars

# Fetch single city
data = ingestor.fetch_city_weather("Jakarta")

# Save raw data
ingestor.save_raw_data(data, "Jakarta")

# Run full ingest
successful_count = ingestor.run()
```

### Database Module

#### `src.database.init_db`

```python
from src.database.init_db import create_tables

# Initialize database
success = create_tables()  # Returns bool
```

#### `src.database.insert_data`

```python
from src.database.insert_data import RawDataInserter

inserter = RawDataInserter()
inserted_count = inserter.run()  # Returns int
```

### Transform Module

#### `src.transform.clean_transform`

```python
from src.transform.clean_transform import DataCleaner

cleaner = DataCleaner()
processed_count = cleaner.run()  # Returns int
```

#### `src.transform.daily_batch`

```python
from src.transform.daily_batch import DailyAggregator

aggregator = DailyAggregator()
aggregated_count = aggregator.run()  # Returns int
```

### Analysis Module

#### `src.analysis.city_ispa_joined`

```python
from src.analysis.city_ispa_joined import CityISPAJoiner

joiner = CityISPAJoiner()
processed_count = joiner.run()  # Returns int
```

### Dashboard Module

#### `dashboard.py` (Streamlit)

```python
# Run dashboard
streamlit run dashboard.py

# Access at http://localhost:8501
```

---

## Database Queries

### Views & Aggregations

#### Most Polluted Cities

```sql
SELECT city, province, pm25_yearly, pm10_yearly
FROM city_ispa_joined
ORDER BY pm25_yearly DESC
LIMIT 10;
```

#### ISPA Correlation

```sql
SELECT 
    CORR(pm25_yearly, prevalence_2023) AS correlation,
    STDDEV(pm25_yearly) AS pm25_stddev,
    STDDEV(prevalence_2023) AS ispa_stddev
FROM city_ispa_joined;
```

#### Daily Statistics by City

```sql
SELECT 
    city,
    DATE(timestamp) as date,
    COUNT(*) as readings,
    AVG(pm25) as pm25_avg,
    MAX(pm25) as pm25_max,
    MIN(pm25) as pm25_min,
    STDDEV(pm25) as pm25_stddev
FROM clean_air_quality
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY city, DATE(timestamp)
ORDER BY date DESC, pm25_avg DESC;
```

#### Latest Data per City

```sql
SELECT DISTINCT ON (city) 
    city, timestamp, pm25, pm10, aqi, temperature, humidity
FROM clean_air_quality
ORDER BY city, timestamp DESC;
```

#### Province-Level Summary

```sql
SELECT 
    province,
    COUNT(DISTINCT city) as city_count,
    AVG(pm25_yearly) as avg_pm25,
    MAX(pm25_yearly) as max_pm25,
    AVG(prevalence_2023) as avg_ispa
FROM city_ispa_joined
GROUP BY province
ORDER BY avg_pm25 DESC;
```

#### Data Quality Report

```sql
SELECT 
    'raw_air_quality' as table_name,
    COUNT(*) as row_count,
    COUNT(DISTINCT city) as cities,
    MAX(timestamp) as latest,
    MIN(timestamp) as oldest
FROM raw_air_quality
UNION ALL
SELECT 
    'clean_air_quality',
    COUNT(*),
    COUNT(DISTINCT city),
    MAX(timestamp),
    MIN(timestamp)
FROM clean_air_quality;
```

### Maintenance Queries

#### Remove Duplicates

```sql
DELETE FROM raw_air_quality
WHERE id NOT IN (
    SELECT MIN(id)
    FROM raw_air_quality
    GROUP BY city, timestamp
);
```

#### Optimize Tables

```sql
REINDEX TABLE raw_air_quality;
REINDEX TABLE clean_air_quality;
REINDEX TABLE daily_air_quality;
REINDEX TABLE city_ispa_joined;

VACUUM ANALYZE;
```

#### Truncate Tables (Reset Database)

```sql
TRUNCATE TABLE raw_air_quality CASCADE;
TRUNCATE TABLE clean_air_quality CASCADE;
TRUNCATE TABLE daily_air_quality CASCADE;
TRUNCATE TABLE city_ispa_joined CASCADE;
```

---

## Configuration API

### Environment Variables

```env
# Required
POSTGRES_USER=airquality_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=air_quality_monitoring
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
WEATHER_API_KEY=your_weatherapi_key

# Optional
LOG_LEVEL=INFO
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
```

### Configuration YAML Structure

```yaml
# config/settings.yaml

cities:
  - Jakarta
  - Surabaya
  - Bandung
  - Medan
  - Semarang

weather_api:
  base_url: "https://api.weatherapi.com/v1/current.json"
  aqi: "yes"
  timeout: 10

interval_minutes: 60

paths:
  raw_data: "data/raw"
  processed_data: "data/processed"
  logs: "data/logs"
```

### City Mapping YAML Structure

```yaml
# config/city_to_province.yaml

Jakarta: DKI Jakarta
Surabaya: Jawa Timur
Bandung: Jawa Barat
Medan: Sumatera Utara
Semarang: Jawa Tengah
# ... more cities
```

---

## Logging API

### Log Levels

```python
logger.debug("Debug message")      # Level 10 - Detailed info
logger.info("Info message")        # Level 20 - General info
logger.warning("Warning message")  # Level 30 - Warnings
logger.error("Error message")      # Level 40 - Errors
logger.critical("Critical")        # Level 50 - Critical
```

### Log Format

```
Console:
2024-12-01 15:30:45 - module.name - INFO - Message here

File:
2024-12-01 15:30:45 - module.name - INFO - [file.py:42] - Message here
```

### Log Locations

```
data/logs/app_20241201.log
data/logs/app_20241202.log
# New log file created daily
```

### Accessing Logs

```bash
# View latest logs
tail -f data/logs/app_*.log

# Search for errors
grep ERROR data/logs/app_*.log

# Count log entries
wc -l data/logs/app_*.log

# View specific module logs
grep "database" data/logs/app_*.log
```

---

## Error Handling

### Custom Exceptions

```python
from src.utils.db_connection import DatabaseConnectionError
from src.utils.config import ConfigError
from src.ingest.weather_ingest import WeatherAPIError

# Database error
try:
    conn = get_db_connection(**creds)
except DatabaseConnectionError as e:
    logger.error(f"Cannot connect: {e}")

# Configuration error
try:
    config = load_config()
except ConfigError as e:
    logger.error(f"Config error: {e}")

# API error
try:
    data = ingestor.fetch_city_weather("Jakarta")
except WeatherAPIError as e:
    logger.error(f"API error: {e}")
```

---

## Performance Tips

### Query Optimization

1. **Use LIMIT for large results**
   ```sql
   SELECT * FROM clean_air_quality LIMIT 1000;
   ```

2. **Filter by date range**
   ```sql
   WHERE timestamp >= NOW() - INTERVAL '30 days'
   ```

3. **Use indexes**
   - Already created in init_db.py
   - Indexes on city, timestamp, date

4. **Batch operations**
   ```python
   execute_batch_insert(conn, query, data_list)
   ```

### Dashboard Caching

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # Database query
    return results
```

---

## Monitoring

### Health Checks

```bash
# Database connection
psql -h localhost -U airquality_user -d air_quality_monitoring -c "SELECT 1"

# API availability
curl -s https://api.weatherapi.com/v1/current.json?key=KEY&q=Jakarta&aqi=yes

# Service health
ps aux | grep python
```

### Metrics to Monitor

- Pipeline execution time
- Database query performance
- API response time
- Error rates
- Data freshness

---

## Contributing

When adding new API functionality:

1. Add docstrings
2. Create tests
3. Update this API reference
4. Follow existing patterns
5. Add logging

---

**Last Updated**: December 2024
