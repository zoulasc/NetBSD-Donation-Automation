"""This module contains functions to send emails to donors."""
import smtplib
import ssl
import logging
from configparser import ConfigParser
from validate_email import validate_email


def sendmail(donations):
    """
    This function sends an email using the SMTP server configured in config.ini.
    """

    # Read configuration from config.ini
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")

    smtp_server = config["smtp"]["server"]
    port_no = config["smtp"]["port"]
    sender_email = config["email"]["sender"]

    # Get sender password from environment variable
    sender_password = config["email"]["password"]
    ack_text = config["msg"]["text"]
    context = ssl.create_default_context()

    # Try to login to server
    try:
        server = smtplib.SMTP_SSL(smtp_server, int(port_no), context=context)
        server.login(sender_email, sender_password)
    except smtplib.SMTPException as error:
        logging.warning(f"Error occurred while sending email: {error}")
        server.quit()

    for donation in donations:
        if not validate_email(donation.email):
            logging.warning(f"Invalid email address: {donation.email}")
            continue

        receiver_email = "ahmet@goksu.in"  # donation.email TODO !FOR TEST PURPOSES!
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
            continue

    server.quit()
