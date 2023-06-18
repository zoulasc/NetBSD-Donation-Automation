import json
import requests
import logging
from datetime import datetime
from models import Donation
from typing import Dict, List

# Define a constant for the state file path
STATE_FILE_PATH = "./src/state-paypal.json"

class PaypalAPI:
    def __init__(self, client_id: str, client_secret: str):
        """
        self.api = paypalrestsdk.Api({
            "mode": "sandbox",  # sandbox or live
            "client_id": client_id,
            "client_secret": client_secret
        })
        """
        self.state_file = STATE_FILE_PATH
        self.latest_donation_time = self._get_latest_donation_time()

    def _get_latest_donation_time(self) -> int:
        """
        Returns the timestamp of the latest donation. If the state file does not exist, returns 0.
        """
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                return state.get("latest_donation_time", 0)
        except FileNotFoundError:
            return 0

    def _update_latest_donation_time(self, timestamp: int):
        self.latest_donation_time = max(int(self.latest_donation_time), int(timestamp))
        with open(self.state_file, "w") as f:
            json.dump({"latest_donation_time": self.latest_donation_time}, f)

    def get_new_donations(self) -> List[Donation]:
        """
        Retrieves new donations from PayPal.
        """
        # TODO: Implement function using PayPal's API

    def _transaction_to_donation(self, transaction, payer_info):
        """
        Converts a PayPal transaction and payer_info into a Donation object.
        Also updates the latest_donation_time based on the transaction's timestamp.
        """
        # TODO: Implement function
