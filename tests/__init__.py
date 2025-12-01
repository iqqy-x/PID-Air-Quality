"""
Unit tests for air quality monitoring system
"""

import pytest
import os
from dotenv import load_dotenv

# Load environment for tests
load_dotenv()

@pytest.fixture
def db_credentials():
    """Fixture for database credentials from environment."""
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "database": os.getenv("POSTGRES_DB", "air_quality_monitoring"),
        "user": os.getenv("POSTGRES_USER", "airquality_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "airquality_pass"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
    }


@pytest.fixture
def sample_city_data():
    """Fixture for sample city data."""
    return {
        "city": "Jakarta",
        "province": "DKI Jakarta",
        "pm25_yearly": 35.5,
        "pm10_yearly": 60.2,
        "aqi_yearly": 75.0,
        "temp_yearly": 26.5,
        "humidity_yearly": 72.0,
        "prevalence_2023": 12.5,
    }
