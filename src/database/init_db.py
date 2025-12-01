"""
Database initialization module for creating required tables and schema.
"""

import os
from dotenv import load_dotenv
from src.utils.db_connection import get_db_connection, close_db_connection, DatabaseConnectionError
from src.utils.config import get_db_credentials, ConfigError
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# SQL statements for table creation
SQL_CREATE_RAW_AIR_QUALITY = """
    CREATE TABLE IF NOT EXISTS raw_air_quality (
        id SERIAL PRIMARY KEY,
        city VARCHAR(50) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
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
        raw_json JSONB,
        file_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(timestamp, city, file_name)
    );
"""

SQL_CREATE_CLEAN_AIR_QUALITY = """
    CREATE TABLE IF NOT EXISTS clean_air_quality (
        id SERIAL PRIMARY KEY,
        city VARCHAR(50) NOT NULL,
        timestamp TIMESTAMP NOT NULL UNIQUE,
        pm25 FLOAT,
        pm10 FLOAT,
        o3 FLOAT,
        no2 FLOAT,
        so2 FLOAT,
        co FLOAT,
        aqi FLOAT,
        temperature FLOAT,
        humidity FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

SQL_CREATE_DAILY_AIR_QUALITY = """
    CREATE TABLE IF NOT EXISTS daily_air_quality (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        city VARCHAR(50) NOT NULL,
        pm25_avg FLOAT,
        pm10_avg FLOAT,
        aqi_avg FLOAT,
        temp_avg FLOAT,
        humidity_avg FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, city)
    );
"""

SQL_CREATE_CITY_ISPA_JOINED = """
    CREATE TABLE IF NOT EXISTS city_ispa_joined (
        id SERIAL PRIMARY KEY,
        city VARCHAR(50) NOT NULL UNIQUE,
        province VARCHAR(50) NOT NULL,
        pm25_yearly FLOAT,
        pm10_yearly FLOAT,
        aqi_yearly FLOAT,
        temp_yearly FLOAT,
        humidity_yearly FLOAT,
        prevalence_2023 FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

SQL_CREATE_ISPA_PROVINCE = """
    CREATE TABLE IF NOT EXISTS ispa_province (
        id SERIAL PRIMARY KEY,
        province VARCHAR(50) NOT NULL UNIQUE,
        prevalence_2023 FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

# Create indexes for better query performance
SQL_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_raw_city_timestamp ON raw_air_quality(city, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_clean_city_timestamp ON clean_air_quality(city, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_daily_date_city ON daily_air_quality(date, city);",
]


def create_tables() -> bool:
    """
    Create all required database tables with proper schema.
    
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        logger.info("Starting database initialization...")
        
        # Get credentials
        credentials = get_db_credentials()
        
        # Connect to database
        conn = get_db_connection(**credentials)
        cur = conn.cursor()
        
        # Create tables
        tables = [
            ("raw_air_quality", SQL_CREATE_RAW_AIR_QUALITY),
            ("clean_air_quality", SQL_CREATE_CLEAN_AIR_QUALITY),
            ("daily_air_quality", SQL_CREATE_DAILY_AIR_QUALITY),
            ("ispa_province", SQL_CREATE_ISPA_PROVINCE),
            ("city_ispa_joined", SQL_CREATE_CITY_ISPA_JOINED),
        ]
        
        for table_name, sql in tables:
            try:
                cur.execute(sql)
                logger.info(f"Table '{table_name}' created or already exists")
            except Exception as e:
                logger.error(f"Failed to create table '{table_name}': {e}")
                conn.rollback()
                return False
        
        # Create indexes
        for sql in SQL_CREATE_INDEXES:
            try:
                cur.execute(sql)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
        
        conn.commit()
        logger.info("✓ All tables and indexes created successfully!")
        return True
        
    except (DatabaseConnectionError, ConfigError) as e:
        logger.error(f"Configuration or connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during table creation: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        close_db_connection(conn)


if __name__ == "__main__":
    success = create_tables()
    exit(0 if success else 1)
