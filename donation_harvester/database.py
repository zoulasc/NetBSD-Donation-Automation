"""
This module contains functions to establish connection with the database
and insert donation details into the database.
"""
import datetime
import logging
import psycopg2
from models import Donation


# SQL Query to insert donation_details into the database
INSERT_DATABASE = """
INSERT INTO netbsd.donation_details VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

# SQL Query to get the last inserted donation_details from the database
LAST_DONATION = """
(
  SELECT datetime
  FROM netbsd.donation_details
  WHERE vendor = 'PayPal'
  ORDER BY datetime DESC
  LIMIT 1
)
UNION
(
  SELECT datetime
  FROM netbsd.donation_details
  WHERE vendor = 'Stripe'
  ORDER BY datetime DESC
  LIMIT 1
);
"""

# SQL Query to get donations from the database within a date range
GET_DONATIONS_IN_RANGE = """
SELECT *
FROM netbsd.donation_details
WHERE datetime BETWEEN %s AND %s AND vendor in %s
ORDER BY datetime DESC;
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
        logging.info("Connected to database.")
        return conn
    except psycopg2.Error as error:
        logging.warning(f"Error while connecting to PostgreSQL: {error}")
        return 0


def get_last_donation_time() -> list[Donation]:
    """Get last donation for both Stripe and Paypal from the database."""
    conn = get_db_connection()

    if conn is None:
        logging.warning("Failed to establish database connection.")
        return 0

    conn.autocommit = True

    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute the query
        cur.execute(LAST_DONATION)
        result = cur.fetchall()
        
        if result == []:
            result = [("2020-01-01 23:59:59+03",), ("2020-01-01 23:59:59+03",)]
            logging.warning(f"No data to fetch, default last donation time is {result}")
        logging.info(f"Successfully fetched last donation time from database: {result}")
        return result  # return a default value if no result is returned

    except psycopg2.Error as error:
        logging.warning(f"Error while executing query: {error}")
        return []
    finally:
        # Close communication with the database
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_donation(donations: list[Donation]) -> int:
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
            logging.info(f"Successfully inserted {donation.confirmation_number} | {donation.email} from {donation.vendor} into database.")
        conn.commit()
        logging.info(
            f"Successfully inserted {len(donations)} donation details into database."
        )
        return 1

    except psycopg2.Error as error:
        logging.exception(f"Error while executing query: {error}")
        return 0
    finally:
        # Close communication with the database
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_donations_in_range(begin_date: datetime, end_date: datetime, vendor: str) -> list[Donation]:
    """Query the database for donations within a date range."""
    conn = get_db_connection()

    if conn is None:
        logging.warning("Failed to establish database connection.")
        return []

    conn.autocommit = True
    donations = []
    try:
        cur = conn.cursor()
        cur.execute(GET_DONATIONS_IN_RANGE, (begin_date, end_date, vendor if vendor else ('Stripe', 'PayPal')))
        rows = cur.fetchall()
        for row in rows:
            donation = Donation(
                confirmation_number=row[0],
                donor_name=row[1],
                currency=row[2],
                quantity=row[3],
                email=row[4],
                vendor=row[5],
                date_time=row[6],
                amount=row[7],
                access_token=row[8],
            )
            donations.append(donation)
            logging.info(f"Successfully fetched {len(donations)} donations from database.")
        return donations

    except psycopg2.Error as error:
        logging.exception(f"Error while executing query: {error}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            