"""
Tests for database connection utilities
"""

import pytest
from src.utils.db_connection import (
    get_db_connection,
    close_db_connection,
    DatabaseConnectionError,
)


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    def test_get_db_connection_success(self, db_credentials):
        """Test successful database connection."""
        try:
            conn = get_db_connection(**db_credentials)
            assert conn is not None
            close_db_connection(conn)
        except DatabaseConnectionError:
            pytest.skip("Database not available for testing")
    
    def test_close_db_connection_safety(self):
        """Test safe closing of None connection."""
        # Should not raise an error
        close_db_connection(None)
    
    def test_invalid_credentials(self):
        """Test connection with invalid credentials."""
        invalid_creds = {
            "host": "invalid_host",
            "database": "invalid_db",
            "user": "invalid_user",
            "password": "invalid_pass",
            "port": 5432,
        }
        
        with pytest.raises(DatabaseConnectionError):
            get_db_connection(**invalid_creds)
