"""This module contains the Stripe API operations."""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List
import stripe
from models import Donation

# Define a constant for conversion factor
CENTS_IN_DOLLAR = 100

# Define a constant for the state file path
STATE_FILE_PATH = "./src/state-stripe.json"


class StripeAPI:
    """This is a class for Paypal API."""

    def __init__(self, api_key: str):
        # Set the API key for stripe
        stripe.api_key = api_key
        # Use the constant defined for the state file path
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
        """This function compares the timestamp of the latest donation with the timestamp of the current donation and updates the latest_donation_time if the current donation is newer."""
        self.latest_donation_time = max(int(self.latest_donation_time), int(timestamp))
        with open(self.state_file, "w") as f:
            json.dump({"latest_donation_time": self.latest_donation_time}, f)

    def get_new_donations(self) -> List[Donation]:
        """
        Retrieves new donations from Stripe by Charge.search(QUERY) Checks for the any newer donations.. It raises an exception if any error occurs.
        """
        try:
            charges = stripe.Charge.search(query=f"created>{self.latest_donation_time}")
            donations = [
                # Since Stripe does not provide customer name in charges, we use the query for to customer info.
                self._charge_to_donation(charge, self.get_customer(charge.customer))
                for charge in charges
            ]
            return donations
        except stripe.error.StripeError as e:
            logging.error(f"An error occurred while getting new donations: {str(e)}")

    def get_all_charges(self, limit: int = 10) -> List[Donation]:
        """
        Retrieves all charges from Stripe up to the given limit.
        It raises an exception if any StripeError occurs.
        """
        try:
            charges = stripe.Charge.list(limit=limit)
            donations = [
                # Since Stripe does not provide customer name in charges, we use the query for to customer info.
                self._charge_to_donation(charge, self.get_customer(charge.customer))
                for charge in charges
            ]
            return donations
        except stripe.error.StripeError as e:
            logging.error(f"An error occurred while getting all charges: {str(e)}")

    def get_charge(self, charge_id: str) -> Donation:
        """
        Retrieves a single charge from Stripe.
        This function is not in use but stays fancy here.
        """
        try:
            charge = stripe.Charge.retrieve(charge_id)
            customer = self.get_customer(charge.customer)
            return self._charge_to_donation(charge, customer)
        except stripe.error.StripeError as e:
            logging.error(f"An error occurred while getting a single charge: {str(e)}")

    def get_customer(self, cus_id: str) -> Dict[str, str]:
        """
        Retrieves a customer from Stripe. If cus_id is None, it returns a default dict.
        It raises an exception if any StripeError occurs.
        """
        if cus_id is None:
            return {"name": None, "email": None}

        try:
            customer = stripe.Customer.retrieve(cus_id)
            return {"name": customer.name, "email": customer.email}
        except stripe.error.StripeError as e:
            logging.error(f"An error occurred while getting a customer: {str(e)}")

    def _charge_to_donation(self, charge, customer):
        """
        Converts a Stripe charge and customer into a Donation object.
        Also updates the latest_donation_time based on the charge's timestamp.
        Uses UTC.
        """
        donor_name = customer.get("name", "Unknown")
        amount = charge.amount / CENTS_IN_DOLLAR if charge.amount else 0.0
        currency = charge.currency if charge.currency else "Unknown"
        email = customer.get("email", "Unknown")
        date_time = (
            datetime.fromtimestamp(charge.created, tz=timezone.utc)
            if charge.created
            else None
        )
        vendor = "Stripe"

        self._update_latest_donation_time(charge.created)
        return Donation(donor_name, amount, currency, email, date_time, vendor)
