"""
Module for cleaning and transforming raw data into clean format.
"""

from dotenv import load_dotenv

from src.utils.db_connection import (
    get_db_connection,
    close_db_connection,
    execute_query,
    DatabaseConnectionError,
)
from src.utils.config import get_db_credentials, ConfigError
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class DataCleaner:
    """Handles data cleaning and transformation."""
    
    def __init__(self):
        """Initialize the cleaner."""
        try:
            self.db_creds = get_db_credentials()
            logger.info("DataCleaner initialized")
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
    
    def get_new_raw_records(self, conn) -> list:
        """
        Get raw records that haven't been cleaned yet.
        
        Args:
            conn: Database connection
            
        Returns:
            List of raw records
        """
        try:
            query = """
                SELECT *
                FROM raw_air_quality
                WHERE timestamp NOT IN (
                    SELECT timestamp FROM clean_air_quality
                )
                ORDER BY timestamp
                LIMIT 10000;
            """
            
            results = execute_query(conn, query, fetch=True)
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error fetching raw records: {e}")
            return []
    
    def clean_and_insert_record(self, conn, row) -> bool:
        """
        Clean a single record and insert into clean table.
        
        Args:
            conn: Database connection
            row: Raw record dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO clean_air_quality
                (city, timestamp, pm25, pm10, o3, no2, so2, co, aqi, temperature, humidity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp) DO NOTHING;
            """
            
            params = (
                row["city"],
                row["timestamp"],
                row["pm25"],
                row["pm10"],
                row["o3"],
                row["no2"],
                row["so2"],
                row["co"],
                row["us_epa_index"],
                row["temperature"],
                row["humidity"],
            )
            
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            
            logger.debug(f"✓ Cleaned {row['city']} at {row['timestamp']}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning record for {row.get('city')}: {e}")
            conn.rollback()
            return False
    
    def run(self) -> int:
        """
        Run the cleaning process on all new raw data.
        
        Returns:
            Number of records cleaned
        """
        logger.info("=" * 50)
        logger.info("Starting Data Cleaning & Transformation")
        logger.info("=" * 50)
        
        conn = None
        processed_count = 0
        
        try:
            conn = get_db_connection(**self.db_creds)
            
            # Get new raw records
            raw_records = self.get_new_raw_records(conn)
            logger.info(f"Found {len(raw_records)} NEW raw records to clean")
            
            if not raw_records:
                logger.info("No new records to clean")
                return 0
            
            for row in raw_records:
                if self.clean_and_insert_record(conn, row):
                    processed_count += 1
            
            logger.info("=" * 50)
            logger.info(f"Cleaning completed: {processed_count}/{len(raw_records)} records")
            logger.info("=" * 50)
            
            return processed_count
            
        except (DatabaseConnectionError, ConfigError) as e:
            logger.error(f"Cannot start cleaning: {e}")
            return 0
        finally:
            close_db_connection(conn)


def clean_transform():
    """Main entry point for data cleaning."""
    try:
        cleaner = DataCleaner()
        cleaner.run()
    except ConfigError as e:
        logger.error(f"Cannot start cleaning: {e}")
        raise


if __name__ == "__main__":
    clean_transform()
