"""This module contains the Paypal API operations."""
import logging
from datetime import datetime, timezone
import requests
from requests.auth import HTTPBasicAuth
from models import Donation


class PaypalAPI:
    """This is a class for Paypal API."""

    def __init__(
        self, client_id: str, client_secret: str, last_donation_time: int
    ) -> None:
        # Get access token
        self.access_token = self._get_access_token(client_id, client_secret)
        self.latest_donation_time = int(last_donation_time)
        
    def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """Gets access token from Paypal API."""
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        payload = "grant_type=client_credentials"
        r = requests.post(
            url,
            auth=HTTPBasicAuth(client_id, client_secret),
            data=payload,
            timeout=10,
        )
        return r.json()["access_token"]

    def _update_latest_donation_time(self, timestamp: int):
        """
        This function compares the timestamp of the latest donation with
        the timestamp of the current donation and updates
        the latest_donation_time if the current donation is newer.
        """
        self.latest_donation_time = max(
            self.latest_donation_time, timestamp
        )

    def get_new_donations(self) -> list[Donation]:
        """
        Gets donation later than the latest_donation_time.
        """
        return self.request_donations(
            self.latest_donation_time
        )

    def get_all_charges(self) -> list[Donation]:
        """
        Gets all charges in 1 month
        """
        return self.request_donations()

    def request_donations(
        self, start_date: int = 0, end_date: int = int(datetime.now().timestamp())
    ) -> list[Donation]:
        """
        This function requests donations from Paypal API for the time between
        given args. If args are not given, it requests donations for the last
        30 days.
        """
        if start_date == 0:
            start_date = end_date - 2419200 # 1 month in seconds becuase Paypal API requires start_date to be at most 31 days before end_date

        headers = {"Authorization": f"Bearer {self.access_token}"}

        # if difference is more than a month adjust start_date to be exactly
        # a month before end_date
        if (end_date - start_date) > 2419200:
            start_date = end_date - 2419200

        # convert datetime object to required format for API
        start_date = datetime.fromtimestamp(start_date).strftime("%Y-%m-%dT%H:%M:%S.999Z")
        end_date = datetime.fromtimestamp(end_date).strftime("%Y-%m-%dT%H:%M:%S.999Z")

        params = (
            ("fields", "payer_info"),
            ("start_date", start_date),
            ("end_date", end_date),
        )

        response = requests.get(
            "https://api-m.sandbox.paypal.com/v1/reporting/transactions",
            headers=headers,
            params=params,
            timeout=10,
        )

        response_json = response.json()

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
        logging.info(f"PayPal - fetched {len(donations)} donations between {start_date} and {end_date}")
        return donations

    def _transaction_to_donation(self, transaction: dict[str, str]) -> Donation:
        """
        Converts a PayPal transaction into a Donation object.
        Also updates the latest_donation_time based on the transaction's
        timestamp.
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
        date_time = datetime.strptime(
            transaction_info["transaction_initiation_date"],
            "%Y-%m-%dT%H:%M:%S%z",
        )
        date_time = int(date_time.astimezone(timezone.utc).timestamp())  # convert to UTC
        vendor = "PayPal"
        # Update the latest_donation_time if this transaction is newer
        self._update_latest_donation_time(date_time)
        return Donation(
            donor_name, amount, currency, email, date_time, vendor
        )
