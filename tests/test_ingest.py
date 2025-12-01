"""
Tests for weather ingest functionality
"""

import pytest
from src.ingest.weather_ingest import WeatherIngestor, WeatherAPIError
from src.utils.config import ConfigError


class TestWeatherIngest:
    """Test weather ingestion functionality."""
    
    def test_ingestor_initialization(self):
        """Test WeatherIngestor initialization."""
        try:
            ingestor = WeatherIngestor()
            assert ingestor is not None
            assert len(ingestor.cities) > 0
            assert ingestor.base_url is not None
        except ConfigError:
            pytest.skip("Configuration not available")
    
    def test_ingestor_with_invalid_config(self, monkeypatch):
        """Test ingestor with missing API key."""
        monkeypatch.delenv("WEATHER_API_KEY", raising=False)
        
        with pytest.raises(ConfigError):
            WeatherIngestor()
    
    @pytest.mark.slow
    def test_fetch_real_data(self):
        """Test fetching real data from API (slow test)."""
        try:
            ingestor = WeatherIngestor()
            data = ingestor.fetch_city_weather("Jakarta")
            
            if data:
                assert "location" in data
                assert "current" in data
        except ConfigError:
            pytest.skip("Configuration not available")
