"""mailing.py is the mailing layer for the feedback site."""
import smtplib
import ssl
from configparser import ConfigParser
from typing import Optional
import logging


def sendmail(receiver_email: Optional[str] = None):
    """
    This function sends an email using the SMTP server configured in config.ini.
    If a receiver_email is not provided, it sends to the email defined in config.ini
    """

    # Read configuration from config.ini
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")

    smtp_server = config["smtp"]["server"]
    port_no = config["smtp"]["port"]
    sender_email = config["email"]["sender"]

    # Get sender password from environment variable
    sender_password = config["email"]["password"]  # os.environ.get("PASSWORD")

    # If receiver_email argument is not provided, use the one from config.ini
    if receiver_email is None:
        receiver_email = config["email"]["receiver"]

    ack_text = config["msg"]["text"]

    # Create the SSL context for secure connection
    context = ssl.create_default_context()

    # Try to login to server and send email
    try:
        server = smtplib.SMTP_SSL(smtp_server, int(port_no), context=context)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, ack_text)
    except smtplib.SMTPException as error:
        logging.warning(f"Error occurred while sending email: {error}")
    finally:
        server.quit()
