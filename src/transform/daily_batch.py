"""
Module for daily aggregation of air quality metrics by city.
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


class DailyAggregator:
    """Handles daily aggregation of air quality metrics."""
    
    def __init__(self):
        """Initialize the aggregator."""
        try:
            self.db_creds = get_db_credentials()
            logger.info("DailyAggregator initialized")
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
    
    def get_daily_aggregates(self, conn) -> list:
        """
        Get daily aggregated metrics from clean data.
        
        Args:
            conn: Database connection
            
        Returns:
            List of daily aggregates
        """
        try:
            query = """
                SELECT
                    DATE(timestamp) AS date,
                    city,
                    AVG(pm25) AS pm25_avg,
                    AVG(pm10) AS pm10_avg,
                    AVG(aqi) AS aqi_avg,
                    AVG(temperature) AS temp_avg,
                    AVG(humidity) AS humidity_avg
                FROM clean_air_quality
                GROUP BY DATE(timestamp), city
                ORDER BY DATE(timestamp), city
                LIMIT 10000;
            """
            
            results = execute_query(conn, query, fetch=True)
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error fetching daily aggregates: {e}")
            return []
    
    def record_exists(self, conn, date, city) -> bool:
        """
        Check if daily record already exists.
        
        Args:
            conn: Database connection
            date: Date to check
            city: City name
            
        Returns:
            True if record exists, False otherwise
        """
        try:
            query = "SELECT COUNT(*) FROM daily_air_quality WHERE date=%s AND city=%s"
            cur = conn.cursor()
            cur.execute(query, (date, city))
            count = cur.fetchone()[0]
            cur.close()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking if record exists: {e}")
            return False
    
    def insert_daily_record(self, conn, row) -> bool:
        """
        Insert a daily aggregated record.
        
        Args:
            conn: Database connection
            row: Aggregated record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO daily_air_quality
                (date, city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, city) DO NOTHING;
            """
            
            params = (
                row["date"],
                row["city"],
                row["pm25_avg"],
                row["pm10_avg"],
                row["aqi_avg"],
                row["temp_avg"],
                row["humidity_avg"],
            )
            
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            
            logger.debug(f"✓ Inserted daily summary for {row['city']} on {row['date']}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting daily record: {e}")
            conn.rollback()
            return False
    
    def run(self) -> int:
        """
        Run the daily aggregation process.
        
        Returns:
            Number of records inserted
        """
        logger.info("=" * 50)
        logger.info("Starting Daily Aggregation Process")
        logger.info("=" * 50)
        
        conn = None
        inserted_count = 0
        
        try:
            conn = get_db_connection(**self.db_creds)
            
            # Get daily aggregates
            daily_records = self.get_daily_aggregates(conn)
            logger.info(f"Found {len(daily_records)} daily aggregates to process")
            
            if not daily_records:
                logger.info("No records to aggregate")
                return 0
            
            for row in daily_records:
                if self.insert_daily_record(conn, row):
                    inserted_count += 1
            
            logger.info("=" * 50)
            logger.info(f"Daily aggregation completed: {inserted_count}/{len(daily_records)} records")
            logger.info("=" * 50)
            
            return inserted_count
            
        except (DatabaseConnectionError, ConfigError) as e:
            logger.error(f"Cannot start aggregation: {e}")
            return 0
        finally:
            close_db_connection(conn)


def run_daily_batch():
    """Main entry point for daily aggregation."""
    try:
        aggregator = DailyAggregator()
        aggregator.run()
    except ConfigError as e:
        logger.error(f"Cannot start aggregation: {e}")
        raise


if __name__ == "__main__":
    run_daily_batch()
