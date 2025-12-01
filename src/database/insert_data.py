"""
Module for inserting raw API data into PostgreSQL database.
"""

import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from src.utils.db_connection import (
    get_db_connection,
    close_db_connection,
    execute_insert,
    DatabaseConnectionError,
)
from src.utils.config import load_config, get_db_credentials, ConfigError
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class DataInsertionError(Exception):
    """Raised when data insertion fails."""
    pass


class RawDataInserter:
    """Handles insertion of raw API responses into the database."""
    
    def __init__(self):
        """Initialize the inserter."""
        try:
            self.config = load_config()
            self.raw_path = self.config["paths"]["raw_data"]
            self.db_creds = get_db_credentials()
            logger.info("RawDataInserter initialized")
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
    
    def parse_raw_file(self, file_path: str) -> Optional[dict]:
        """
        Parse and validate raw JSON file.
        
        Args:
            file_path: Path to raw data file
            
        Returns:
            Parsed data or None if invalid
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ["location", "current"]
            if not all(field in data for field in required_fields):
                logger.warning(f"Invalid data structure in {file_path}")
                return None
            
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            return None
    
    def extract_air_quality_data(self, data: dict) -> Optional[dict]:
        """
        Extract air quality metrics from API response.
        
        Args:
            data: Raw API response
            
        Returns:
            Extracted metrics or None if extraction fails
        """
        try:
            location = data.get("location", {})
            current = data.get("current", {})
            air_quality = current.get("air_quality", {})
            
            city = location.get("name")
            timestamp_str = location.get("localtime")
            
            if not city or not timestamp_str:
                logger.warning("Missing city or timestamp in data")
                return None
            
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            
            return {
                "city": city,
                "timestamp": timestamp,
                "temperature": current.get("temp_c"),
                "humidity": current.get("humidity"),
                "wind_speed": current.get("wind_kph"),
                "pm25": air_quality.get("pm2_5"),
                "pm10": air_quality.get("pm10"),
                "o3": air_quality.get("o3"),
                "no2": air_quality.get("no2"),
                "so2": air_quality.get("so2"),
                "co": air_quality.get("co"),
                "us_epa_index": air_quality.get("us-epa-index"),
                "raw_json": json.dumps(data),
            }
        except (KeyError, ValueError) as e:
            logger.error(f"Error extracting data: {e}")
            return None
    
    def check_if_already_inserted(self, conn, file_name: str) -> bool:
        """
        Check if file was already inserted.
        
        Args:
            conn: Database connection
            file_name: Filename to check
            
        Returns:
            True if already inserted, False otherwise
        """
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM raw_air_quality WHERE file_name = %s",
                (file_name,)
            )
            count = cur.fetchone()[0]
            cur.close()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking if file already inserted: {e}")
            return False
    
    def insert_record(self, conn, data: dict, file_name: str) -> bool:
        """
        Insert a single record into the database.
        
        Args:
            conn: Database connection
            data: Extracted data
            file_name: Original filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cur = conn.cursor()
            query = """
                INSERT INTO raw_air_quality
                (city, timestamp, temperature, humidity, wind_speed,
                 pm25, pm10, o3, no2, so2, co, us_epa_index, raw_json, file_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                data["city"],
                data["timestamp"],
                data["temperature"],
                data["humidity"],
                data["wind_speed"],
                data["pm25"],
                data["pm10"],
                data["o3"],
                data["no2"],
                data["so2"],
                data["co"],
                data["us_epa_index"],
                data["raw_json"],
                file_name,
            )
            
            cur.execute(query, params)
            conn.commit()
            cur.close()
            logger.info(f"✓ Inserted {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert {file_name}: {e}")
            conn.rollback()
            return False
    
    def run(self) -> int:
        """
        Process all raw data files and insert into database.
        
        Returns:
            Number of successfully inserted files
        """
        logger.info("=" * 50)
        logger.info("Starting Raw Data Insertion")
        logger.info("=" * 50)
        
        conn = None
        successful_count = 0
        
        try:
            conn = get_db_connection(**self.db_creds)
            
            if not os.path.exists(self.raw_path):
                logger.warning(f"Raw data path does not exist: {self.raw_path}")
                return 0
            
            files = [f for f in os.listdir(self.raw_path) if f.endswith(".json")]
            logger.info(f"Found {len(files)} JSON files to process")
            
            for file_name in files:
                # Skip if already inserted
                if self.check_if_already_inserted(conn, file_name):
                    logger.debug(f"[SKIP] {file_name} already inserted")
                    continue
                
                file_path = os.path.join(self.raw_path, file_name)
                
                # Parse file
                raw_data = self.parse_raw_file(file_path)
                if not raw_data:
                    continue
                
                # Extract data
                extracted_data = self.extract_air_quality_data(raw_data)
                if not extracted_data:
                    continue
                
                # Insert into database
                if self.insert_record(conn, extracted_data, file_name):
                    successful_count += 1
            
            logger.info("=" * 50)
            logger.info(f"Insertion completed: {successful_count}/{len(files)} files")
            logger.info("=" * 50)
            
            return successful_count
            
        except (DatabaseConnectionError, ConfigError) as e:
            logger.error(f"Cannot start insertion: {e}")
            return 0
        finally:
            close_db_connection(conn)


def insert_raw_data():
    """Main entry point for data insertion."""
    try:
        inserter = RawDataInserter()
        inserter.run()
    except ConfigError as e:
        logger.error(f"Cannot start insertion: {e}")
        raise


if __name__ == "__main__":
    insert_raw_data()
