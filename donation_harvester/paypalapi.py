"""This module contains the Paypal API operations."""
import base64
from configparser import ConfigParser
import logging
from datetime import datetime, timezone
import requests
from config.models import Donation

config = ConfigParser()
config.read("config/config.ini", encoding="utf-8")

PAYPAL_TOKEN_URL = config["harvester"]["PAYPAL_TOKEN_URL"]
PAYPAL_TRANSACTION_URL = config["harvester"]["PAYPAL_TRANSACTION_URL"]

class PaypalAPI:
    """This is a class for Paypal API."""
    def __init__(
        self, client_id: str, client_secret: str, last_donation_time: int
    ) -> None:
        # Get access token
        self.access_token = self._get_access_token(client_id, client_secret)
        # Set latest_donation_time to last_donation_time
        # + 1 sec to avoid getting the same donation twice
        self.latest_donation_time = int(last_donation_time) + 1

    def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """Gets access token from Paypal API."""
        url = PAYPAL_TOKEN_URL
        payload = "grant_type=client_credentials"
        headers = {
            'Authorization': 'Basic ' + \
                base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        }
        try:
            r = requests.post(url, headers=headers, data=payload, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request to PayPal API Auth failed: {e}")
            return []
        return r.json()["access_token"]

    def get_new_donations(self) -> list[Donation]:
        """
        Gets donation later than the latest_donation_time.
        """
        return self.request_donations(
            self.latest_donation_time
        )

    def request_donations(
        self, start_date: int = 0, end_date: int = int(datetime.now().timestamp())
    ) -> list[Donation]:
        """
        This function requests donations from Paypal API for the time between
        given args. If args are not given, it requests donations for the last
        30 days.
        """
        if start_date == 0:
            start_date = end_date - 2419200
            # 1 month in seconds becuase Paypal API
            # requires start_date to be at most 31 days before end_date

        # if difference is more than a month adjust start_date to be exactly
        # a month before end_date
        if (end_date - start_date) > 2419200:
            start_date = end_date - 2419200

        # convert datetime object to required format for API
        start_date = datetime.fromtimestamp(start_date, tz=timezone.utc)\
            .strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_date = datetime.fromtimestamp(end_date, tz=timezone.utc)\
            .strftime("%Y-%m-%dT%H:%M:%S.000Z")

        headers = {"Authorization": f"Bearer {self.access_token}"}

        params = (
            ("fields", "payer_info"),
            ("start_date", start_date),
            ("end_date", end_date),
        )

        try:
            r = requests.get(
                PAYPAL_TRANSACTION_URL,
                headers=headers,
                params=params,
                timeout=10,
            )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request to PayPal API failed: {e}")
            return []

        response_json = r.json()

        # Check if the request was successful
        if (
            "name" in response_json
            and response_json["name"] == "INVALID_REQUEST"
        ):
            logging.error(f"Invalid request: {response_json['message']}")
            return []

        # Check if the response contains the transaction_details key
        if "transaction_details" not in response_json:
            logging.error("KeyError: 'transaction_details'")
            return []

        # Get the transactions from the response
        transactions = response_json["transaction_details"]

        # Convert the transactions to Donation objects. Store them in a list.
        donations = []
        for transaction in transactions:
            donation = self._transaction_to_donation(transaction)
            donations.append(donation)
        logging.info(f"PayPal - fetched {len(donations)}\
            donations between {start_date} and {end_date}")
        return donations

    def _transaction_to_donation(self, transaction: dict[str, str]) -> Donation:
        """
        Converts a PayPal transaction into a Donation object.
        Uses UTC.
        """

        # Get the transaction_info and payer_info from the transaction
        transaction_info = transaction["transaction_info"]
        payer_info = transaction["payer_info"]

        # Prepare the variables to return Donation object
        donor_name = payer_info["payer_name"].get(
            "alternate_full_name", "Unknown"
        )
        email = payer_info.get("email_address", "Unknown")
        amount = float(
            transaction_info["transaction_amount"].get("value", 0.0)
        )
        currency = transaction_info["transaction_amount"].get(
            "currency_code", "Unknown"
        )
        date_time = int(datetime.strptime(
            transaction_info["transaction_initiation_date"],
            "%Y-%m-%dT%H:%M:%S%z"
        ).replace(tzinfo=timezone.utc).timestamp())

        vendor = "PayPal"
        return Donation(
            donor_name, amount, currency, email, date_time, vendor
        )
