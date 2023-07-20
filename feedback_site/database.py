"""database.py is the database layer for the feedback site."""
from typing import Any
import logging
import psycopg2

from config import get_db_connection


def execute_query(query: str, *params: Any):
    """
    Execute a query with given parameters and return the result.
    """
    conn = get_db_connection()
    if conn is None:
        logging.warning("Failed to establish database connection.")
        return []

    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute the query with provided parameters
        cur.execute(query, params)

        # Make sure to commit changes for INSERT statements
        if "INSERT" in query:
            conn.commit()
            return 1
        
        # If the query is for getting donors (multiple), use fetchall
        if "SELECT i.name" in query:
            result = cur.fetchall()
            logging.info(f"result: {result}")
            return result
        
        # Fetch one result
        result = cur.fetchone()
        logging.info(f"result: {result}")
        # get rid of tuple and return
        return result[0] if result else None
    except psycopg2.Error as error:
        logging.warning(f"Error while executing query: {error}")
        return []
    finally:
        # Close communication with the database
        if cur:
            cur.close()
        if conn:
            conn.close()
