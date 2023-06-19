"""This module contains functions to establish connection with the database and insert donation details into the database."""
import logging
import psycopg2

INSERT_DATABASE = """
INSERT INTO netbsd.donation_details VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

# Define connection parameters
DB_CONFIG = {
    "database": "test_database",
    "user": "test_user",
    "password": "test@123",
    "host": "127.0.0.1",
    "port": "5432",
}


def get_db_connection() -> psycopg2.extensions.connection:
    """
    Establish and return a connection with the database.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as error:
        logging.warning(f"Error while connecting to PostgreSQL: {error}")
        return 0


def insert_donation(donations) -> int:
    """Insert donation details into the database."""
    conn = get_db_connection()

    if conn is None:
        logging.warning("Failed to establish database connection.")
        return 0

    conn.autocommit = True

    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute the query with provided parameters
        for donation in donations:
            cur.execute(
                INSERT_DATABASE,
                (
                    donation.confirmation_number,
                    donation.donor_name,
                    donation.currency,
                    donation.quantity,
                    donation.email,
                    donation.vendor,
                    donation.date_time,
                    donation.amount,
                    donation.access_token,
                ),
            )

        conn.commit()
        logging.info(
            f"Successfully inserted {donations.count} donation details into database."
        )
        return 1

    except psycopg2.Error as error:
        logging.warning(f"Error while executing query: {error}")
        return 0
    finally:
        # Close communication with the database
        if cur:
            cur.close()
        if conn:
            conn.close()
