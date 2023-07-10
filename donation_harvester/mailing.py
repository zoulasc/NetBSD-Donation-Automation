"""This module contains functions to send emails to donors."""

import smtplib
import ssl
import logging

from configparser import ConfigParser
from validate_email import validate_email
from database import insert_deferred_email
from models import Donation


def sendmail(donations: list[Donation]) -> None:
    """
    This function sends an email using the SMTP server configured in config.ini.
    """

    # Read configuration from config.ini
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")

    smtp_server = config["smtp"]["server"]
    port_no = int(config["smtp"]["port"])
    smtp_login = config["smtp"]["login"]
    smtp_password = config["smtp"]["password"]

    # Get sender credentials from environment variable
    sender_email = config["email"]["sender"]
    debug_receiver_email = config["email"]["receiver"]
    ack_text = config["msg"]["text"]

    # Try to login to server
    try:
        if port_no == 25:
            server = smtplib.SMTP(smtp_server, port_no)
        else:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_server, port_no, context=context)
            server.login(smtp_login, smtp_password)
    except (smtplib.SMTPException, OSError) as error:
        logging.warning(f"Error occurred while sending email: {error}")

        # Insert deferred emails into database to send them later
        insert_deferred_email(donations)

        return

    logging.info(f"Logged in to {smtp_server} successfully.")
    failed_donations = []
    for donation in donations:
        if not validate_email(donation.email):
            logging.warning(
                f"Invalid email address: {donation.email}, skipping..."
            )
            continue

        if debug_receiver_email == "":
            receiver_email = donation.email
        else:
            receiver_email = debug_receiver_email
        # Create the email message
        msg = ack_text.format(
            donor_name=donation.donor_name,
            amount=donation.amount,
            currency=donation.currency,
            confirmation_number=donation.confirmation_number,
            access_token=donation.access_token,
        )

        try:
            server.sendmail(sender_email, receiver_email, msg)
            logging.info(f"mail sent to {donation.email}")
        except smtplib.SMTPException as error:
            logging.warning(f"Error occurred while sending email: {error}")
            failed_donations.append(donation)
            continue

    if failed_donations:
        insert_deferred_email(failed_donations)

    server.quit()
