"""
Database connection utilities for PostgreSQL operations.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
from .logger import get_logger

logger = get_logger(__name__)


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


def get_db_connection(
    host: str,
    database: str,
    user: str,
    password: str,
    port: int = 5432,
) -> psycopg2.extensions.connection:
    """
    Create and return a PostgreSQL database connection.
    
    Args:
        host: Database host address
        database: Database name
        user: Database user
        password: Database password
        port: Database port (default: 5432)
        
    Returns:
        psycopg2 connection object
        
    Raises:
        DatabaseConnectionError: If connection fails
    """
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            connect_timeout=10,
        )
        logger.info(f"Connected to database: {database}@{host}:{port}")
        return conn
    except psycopg2.OperationalError as e:
        error_msg = f"Failed to connect to database at {host}:{port} - {str(e)}"
        logger.error(error_msg)
        raise DatabaseConnectionError(error_msg) from e


def close_db_connection(conn: Optional[psycopg2.extensions.connection]) -> None:
    """
    Close database connection safely.
    
    Args:
        conn: Database connection object
    """
    if conn:
        try:
            conn.close()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.warning(f"Error closing database connection: {e}")


def execute_query(
    conn: psycopg2.extensions.connection,
    query: str,
    params: tuple = None,
    fetch: bool = False,
    fetch_one: bool = False,
) -> Optional[Any]:
    """
    Execute a database query with error handling.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters for safe parameterization
        fetch: Whether to fetch all results
        fetch_one: Whether to fetch only one result
        
    Returns:
        Query results if fetch/fetch_one is True, otherwise None
        
    Raises:
        Exception: If query execution fails
    """
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
            
        if fetch:
            result = cur.fetchall()
        elif fetch_one:
            result = cur.fetchone()
        else:
            result = None
            
        cur.close()
        return result
        
    except psycopg2.Error as e:
        logger.error(f"Database query error: {e}")
        raise


def execute_insert(
    conn: psycopg2.extensions.connection,
    query: str,
    params: tuple,
) -> bool:
    """
    Execute an INSERT query with automatic commit.
    
    Args:
        conn: Database connection
        query: SQL INSERT query
        params: Parameters for the query
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        logger.debug(f"Insert executed successfully")
        return True
    except psycopg2.Error as e:
        logger.error(f"Insert failed: {e}")
        conn.rollback()
        return False


def execute_batch_insert(
    conn: psycopg2.extensions.connection,
    query: str,
    data: list,
) -> int:
    """
    Execute batch INSERT with multiple records.
    
    Args:
        conn: Database connection
        query: SQL INSERT query
        data: List of tuples containing records
        
    Returns:
        Number of rows inserted
    """
    try:
        cur = conn.cursor()
        cur.executemany(query, data)
        conn.commit()
        rows_inserted = cur.rowcount
        cur.close()
        logger.info(f"Batch insert completed: {rows_inserted} rows inserted")
        return rows_inserted
    except psycopg2.Error as e:
        logger.error(f"Batch insert failed: {e}")
        conn.rollback()
        return 0
