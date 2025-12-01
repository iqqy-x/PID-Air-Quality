"""
Tests for configuration management
"""

import pytest
import os
import tempfile
import yaml
from src.utils.config import load_config, load_city_mapping, ConfigError


class TestConfigLoading:
    """Test configuration loading functionality."""
    
    def test_load_existing_config(self):
        """Test loading existing configuration."""
        try:
            config = load_config()
            assert isinstance(config, dict)
            assert "cities" in config
            assert "weather_api" in config
            assert "paths" in config
        except ConfigError:
            pytest.skip("Configuration file not available")
    
    def test_load_nonexistent_config(self):
        """Test loading nonexistent configuration."""
        with pytest.raises(ConfigError):
            load_config("nonexistent_config.yaml")
    
    def test_cities_in_config(self):
        """Test that required cities are in configuration."""
        try:
            config = load_config()
            cities = config.get("cities", [])
            assert len(cities) > 0
            assert "Jakarta" in cities
        except ConfigError:
            pytest.skip("Configuration file not available")
    
    def test_load_city_mapping(self):
        """Test loading city to province mapping."""
        try:
            mapping = load_city_mapping()
            assert isinstance(mapping, dict)
            assert len(mapping) > 0
        except ConfigError:
            pytest.skip("City mapping file not available")
