"""
Weather API data ingestion module for collecting air quality and weather data.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from src.utils.config import load_config, ConfigError
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class WeatherAPIError(Exception):
    """Raised when WeatherAPI request fails."""
    pass


class WeatherIngestor:
    """Handles fetching and saving weather data from WeatherAPI."""
    
    def __init__(self):
        """Initialize the ingestor with configuration."""
        try:
            self.api_key = os.getenv("WEATHER_API_KEY")
            if not self.api_key:
                raise ConfigError("WEATHER_API_KEY environment variable not set")
            
            self.config = load_config()
            self.cities = self.config.get("cities", [])
            self.base_url = self.config["weather_api"]["base_url"]
            self.aqi_enabled = self.config["weather_api"].get("aqi", "yes")
            self.raw_path = self.config["paths"]["raw_data"]
            
            os.makedirs(self.raw_path, exist_ok=True)
            logger.info(f"WeatherIngestor initialized with {len(self.cities)} cities")
            
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
    
    def fetch_city_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather and air quality data for a city from WeatherAPI.
        
        Args:
            city: City name to fetch data for
            
        Returns:
            JSON response from API or None if failed
        """
        try:
            params = {
                "key": self.api_key,
                "q": city,
                "aqi": self.aqi_enabled,
            }
            
            logger.debug(f"Fetching data for {city}...")
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✓ Successfully fetched data for {city}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching data for {city}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {city}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {city}: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Invalid API response for {city}: {e}")
            return None
    
    def save_raw_data(self, data: Dict[str, Any], city: str) -> bool:
        """
        Save raw API response to JSON file.
        
        Args:
            data: JSON data from API
            city: City name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.raw_path}/{city}_{timestamp}.json"
            
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✓ Saved raw data: {filename}")
            return True
            
        except IOError as e:
            logger.error(f"Failed to save data for {city}: {e}")
            return False
    
    def run(self) -> int:
        """
        Run the ingestion process for all cities.
        
        Returns:
            Number of successfully ingested cities
        """
        logger.info("=" * 50)
        logger.info("Starting WeatherAPI Ingestion Process")
        logger.info("=" * 50)
        
        successful_count = 0
        failed_cities = []
        
        for city in self.cities:
            try:
                data = self.fetch_city_weather(city)
                
                if data and self.save_raw_data(data, city):
                    successful_count += 1
                else:
                    failed_cities.append(city)
                    
            except Exception as e:
                logger.error(f"Unexpected error for {city}: {e}")
                failed_cities.append(city)
        
        # Summary
        logger.info("=" * 50)
        logger.info(f"Ingestion completed: {successful_count}/{len(self.cities)} cities")
        if failed_cities:
            logger.warning(f"Failed cities: {', '.join(failed_cities)}")
        logger.info("=" * 50)
        
        return successful_count


def run_ingest():
    """Main entry point for ingestion."""
    try:
        ingestor = WeatherIngestor()
        ingestor.run()
    except ConfigError as e:
        logger.error(f"Cannot start ingestion: {e}")
        raise


if __name__ == "__main__":
    run_ingest()
