"""
Module for joining city-level air quality data with ISPA province data.
"""

from typing import Dict, List, Tuple
from dotenv import load_dotenv

from src.utils.db_connection import (
    get_db_connection,
    close_db_connection,
    execute_query,
    DatabaseConnectionError,
)
from src.utils.config import load_city_mapping, get_db_credentials, ConfigError
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class CityISPAJoiner:
    """Handles joining city air quality data with ISPA province data."""
    
    def __init__(self):
        """Initialize the joiner."""
        try:
            self.db_creds = get_db_credentials()
            self.city_to_province = load_city_mapping()
            logger.info(f"CityISPAJoiner initialized with {len(self.city_to_province)} cities")
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
    
    def get_daily_metrics(self, conn) -> list:
        """
        Get all daily aggregated metrics.
        
        Args:
            conn: Database connection
            
        Returns:
            List of daily metrics
        """
        try:
            query = """
                SELECT city, pm25_avg, pm10_avg, aqi_avg, temp_avg, humidity_avg
                FROM daily_air_quality
                ORDER BY city, date DESC;
            """
            
            results = execute_query(conn, query, fetch=True)
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error fetching daily metrics: {e}")
            return []
    
    def aggregate_city_metrics(self, daily_records: list) -> Dict[str, Dict]:
        """
        Aggregate daily metrics to yearly per city.
        
        Args:
            daily_records: List of daily records
            
        Returns:
            Dictionary of aggregated metrics per city
        """
        city_metrics = {}
        
        for record in daily_records:
            city = record.get("city")
            province = self.city_to_province.get(city)
            
            if not province:
                logger.warning(f"City '{city}' not found in province mapping")
                continue
            
            if city not in city_metrics:
                city_metrics[city] = {
                    "province": province,
                    "pm25": [],
                    "pm10": [],
                    "aqi": [],
                    "temperature": [],
                    "humidity": [],
                }
            
            # Append values (skip None values)
            if record.get("pm25_avg") is not None:
                city_metrics[city]["pm25"].append(record["pm25_avg"])
            if record.get("pm10_avg") is not None:
                city_metrics[city]["pm10"].append(record["pm10_avg"])
            if record.get("aqi_avg") is not None:
                city_metrics[city]["aqi"].append(record["aqi_avg"])
            if record.get("temp_avg") is not None:
                city_metrics[city]["temperature"].append(record["temp_avg"])
            if record.get("humidity_avg") is not None:
                city_metrics[city]["humidity"].append(record["humidity_avg"])
        
        logger.info(f"Aggregated metrics for {len(city_metrics)} cities")
        return city_metrics
    
    def calculate_yearly_averages(self, city_metrics: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Calculate yearly averages from aggregated metrics.
        
        Args:
            city_metrics: Dictionary of aggregated metrics
            
        Returns:
            Dictionary of yearly averages
        """
        yearly_data = {}
        
        for city, metrics in city_metrics.items():
            def safe_average(values: list) -> float:
                return sum(values) / len(values) if values else 0.0
            
            yearly_data[city] = {
                "province": metrics["province"],
                "pm25_yearly": safe_average(metrics["pm25"]),
                "pm10_yearly": safe_average(metrics["pm10"]),
                "aqi_yearly": safe_average(metrics["aqi"]),
                "temp_yearly": safe_average(metrics["temperature"]),
                "humidity_yearly": safe_average(metrics["humidity"]),
            }
        
        return yearly_data
    
    def get_province_ispa(self, conn, province: str) -> float:
        """
        Get ISPA prevalence for a province.
        
        Args:
            conn: Database connection
            province: Province name
            
        Returns:
            ISPA prevalence value or 0.0 if not found
        """
        try:
            query = "SELECT prevalence_2023 FROM ispa_province WHERE province = %s"
            cur = conn.cursor()
            cur.execute(query, (province,))
            result = cur.fetchone()
            cur.close()
            
            if result:
                return result[0]
            logger.warning(f"No ISPA data found for province: {province}")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error fetching ISPA data: {e}")
            return 0.0
    
    def clear_old_data(self, conn) -> bool:
        """
        Clear old data before inserting new records.
        
        Args:
            conn: Database connection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM city_ispa_joined;")
            conn.commit()
            cur.close()
            logger.info("Cleared old city_ispa_joined data")
            return True
        except Exception as e:
            logger.error(f"Error clearing old data: {e}")
            conn.rollback()
            return False
    
    def insert_city_ispa_record(self, conn, city: str, data: Dict) -> bool:
        """
        Insert a city-ISPA joined record.
        
        Args:
            conn: Database connection
            city: City name
            data: City metrics and ISPA data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO city_ispa_joined
                (city, province, pm25_yearly, pm10_yearly, aqi_yearly,
                 temp_yearly, humidity_yearly, prevalence_2023)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (city) DO UPDATE SET
                    pm25_yearly = EXCLUDED.pm25_yearly,
                    pm10_yearly = EXCLUDED.pm10_yearly,
                    aqi_yearly = EXCLUDED.aqi_yearly,
                    temp_yearly = EXCLUDED.temp_yearly,
                    humidity_yearly = EXCLUDED.humidity_yearly,
                    prevalence_2023 = EXCLUDED.prevalence_2023,
                    updated_at = CURRENT_TIMESTAMP;
            """
            
            params = (
                city,
                data["province"],
                data["pm25_yearly"],
                data["pm10_yearly"],
                data["aqi_yearly"],
                data["temp_yearly"],
                data["humidity_yearly"],
                data.get("prevalence_2023", 0.0),
            )
            
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            
            logger.debug(f"✓ Inserted/updated {city}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting city_ispa record for {city}: {e}")
            conn.rollback()
            return False
    
    def run(self) -> int:
        """
        Run the city-ISPA join process.
        
        Returns:
            Number of records processed
        """
        logger.info("=" * 50)
        logger.info("Starting City-ISPA Join Process")
        logger.info("=" * 50)
        
        conn = None
        processed_count = 0
        
        try:
            conn = get_db_connection(**self.db_creds)
            
            # Clear old data
            if not self.clear_old_data(conn):
                return 0
            
            # Get daily metrics
            daily_records = self.get_daily_metrics(conn)
            logger.info(f"Found {len(daily_records)} daily records")
            
            if not daily_records:
                logger.warning("No daily records found")
                return 0
            
            # Aggregate metrics
            city_metrics = self.aggregate_city_metrics(daily_records)
            
            # Calculate yearly averages
            yearly_data = self.calculate_yearly_averages(city_metrics)
            logger.info(f"Calculated yearly averages for {len(yearly_data)} cities")
            
            # Insert records with ISPA data
            for city, metrics in yearly_data.items():
                province = metrics["province"]
                ispa_prevalence = self.get_province_ispa(conn, province)
                metrics["prevalence_2023"] = ispa_prevalence
                
                if self.insert_city_ispa_record(conn, city, metrics):
                    processed_count += 1
            
            logger.info("=" * 50)
            logger.info(f"City-ISPA join completed: {processed_count} cities processed")
            logger.info("=" * 50)
            
            return processed_count
            
        except (DatabaseConnectionError, ConfigError) as e:
            logger.error(f"Cannot start city-ISPA join: {e}")
            return 0
        finally:
            close_db_connection(conn)


def build_city_ispa():
    """Main entry point for city-ISPA join."""
    try:
        joiner = CityISPAJoiner()
        joiner.run()
    except ConfigError as e:
        logger.error(f"Cannot start city-ISPA join: {e}")
        raise


if __name__ == "__main__":
    build_city_ispa()