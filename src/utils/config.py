"""
Configuration management for the air quality monitoring system.
"""

import yaml
import os
from typing import Dict, Any
from .logger import get_logger

logger = get_logger(__name__)


class ConfigError(Exception):
    """Raised when configuration loading fails."""
    pass


def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigError: If configuration file not found or invalid
    """
    if not os.path.exists(config_path):
        error_msg = f"Configuration file not found: {config_path}"
        logger.error(error_msg)
        raise ConfigError(error_msg)
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except yaml.YAMLError as e:
        error_msg = f"Failed to parse YAML configuration: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e


def load_city_mapping(mapping_path: str = "config/city_to_province.yaml") -> Dict[str, str]:
    """
    Load city to province mapping.
    
    Args:
        mapping_path: Path to city mapping file
        
    Returns:
        Dictionary mapping cities to provinces
        
    Raises:
        ConfigError: If mapping file not found or invalid
    """
    if not os.path.exists(mapping_path):
        error_msg = f"City mapping file not found: {mapping_path}"
        logger.error(error_msg)
        raise ConfigError(error_msg)
    
    try:
        with open(mapping_path, "r") as f:
            mapping = yaml.safe_load(f)
        
        logger.info(f"City mapping loaded: {len(mapping)} cities")
        return mapping
    except yaml.YAMLError as e:
        error_msg = f"Failed to parse city mapping: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e


def get_db_credentials() -> Dict[str, Any]:
    """
    Get database credentials from environment variables.
    
    Returns:
        Dictionary with database connection parameters
        
    Raises:
        ConfigError: If required environment variables are missing
    """
    required_vars = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ConfigError(error_msg)
    
    return {
        "host": os.getenv("POSTGRES_HOST"),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
    }
