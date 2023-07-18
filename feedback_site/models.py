"""models.py is the database query preperation layer for the feedback site."""
import logging

from database import execute_query
from dbconfig import PREFIX

class Donation:
    """The Donation class represents a donation in the database."""

    SQL_CHECK_EXISTS_BY_EMAIL_AND_CONFIRMATION = f"""
    PREPARE check_donation (text, int) AS
    SELECT EXISTS (
      SELECT 1
      FROM {PREFIX}.information d
      WHERE d.email = $1 AND d.confirmation_no = $2
    );
    EXECUTE check_donation(%s, %s);
    """

    SQL_GET_BY_TOKEN = f"""
    PREPARE get_donation_by_token (text) AS
    SELECT confirmation_no
    FROM {PREFIX}.information
    WHERE uuid = $1;
    EXECUTE get_donation_by_token(%s);
    """

    @classmethod
    def exists_by_email_and_confirmation(cls, email, confirmation_no):
        """Check if a donation exists by email and confirmation number."""
        logging.info(
            f"Check donation by email and confirmation: {email} {confirmation_no}"
        )
        return execute_query(
            cls.SQL_CHECK_EXISTS_BY_EMAIL_AND_CONFIRMATION, email, confirmation_no
        )

    @classmethod
    def get_by_token(cls, token):
        """Get a donation by its token."""
        logging.info(f"Check donation by token: {token}")
        return execute_query(cls.SQL_GET_BY_TOKEN, token)


class Feedback:
    """The Feedback class represents a feedback in the database."""

    SQL_CHECK_EXISTS_BY_CONFIRMATION = f"""
    PREPARE check_feedback (int) AS
    SELECT EXISTS(SELECT 1 FROM {PREFIX}.interaction WHERE confirmation_no = $1);
    EXECUTE check_feedback(%s);
    """

    SQL_INSERT_FEEDBACK = f"""
    PREPARE insert_feedback (int, bool, text, bool, text, bool, text) AS
    INSERT INTO {PREFIX}.interaction VALUES($1, $2, $3, $4, $5, $6, $7);
    EXECUTE insert_feedback(%s, %s, %s, %s, %s, %s, %s);
    """
    
    SQL_GET_DONORS_THIS_YEAR = f""" 
    SELECT i.name, 
        CASE WHEN i.answer2 THEN i.email ELSE NULL END
    FROM {PREFIX}.interaction AS i
    INNER JOIN {PREFIX}.information AS inf 
    ON i.confirmation_no = inf.confirmation_no 
    WHERE i.answer1 = TRUE 
        AND EXTRACT(YEAR FROM TO_TIMESTAMP(inf.datetime)) = %s;
    """

    @classmethod
    def exists_by_confirmation(cls, confirmation_no):
        """Check if a feedback exists by confirmation number."""
        logging.info(f"Check feedback by confirmation: {confirmation_no}")
        return execute_query(cls.SQL_CHECK_EXISTS_BY_CONFIRMATION, confirmation_no)

    @classmethod
    def insert(cls, feedback_info):
        """Insert the feedback into the database."""
        logging.info(f"Insert feedback: {feedback_info}")
        return execute_query(cls.SQL_INSERT_FEEDBACK, *feedback_info.values())
    
    @classmethod
    def get_all_by_year(cls,year):
        """Get donors who wanted to be listed this year."""
        logging.info(f"Get donors this year: {year}")
        return execute_query(cls.SQL_GET_DONORS_THIS_YEAR, year)