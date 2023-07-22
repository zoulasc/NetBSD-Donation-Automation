"""This module contains the Stripe API operations."""
import logging
import stripe
from config.models import Donation

# Define a constant for conversion factor
CENTS_IN_DOLLAR = 100


class StripeAPI:
    """This is a class for Stripe API."""

    def __init__(self, api_key: str, last_donation_time: int) -> None:
        # Set the API key for stripe
        stripe.api_key = api_key

        self.latest_donation_time = last_donation_time + 1

    def get_new_donations(self) -> list[Donation]:
        """
        Retrieves new donations from Stripe by Charge.search(QUERY)
        Checks for the any newer donations.. It raises an exception
        if any error occurs.
        """
        try:
            charges = stripe.Charge.search(
                query=f"created>{self.latest_donation_time}"
            )
            donations = []
            for charge in charges:
                # Since Stripe does not provide customer name in charges,
                # we use the query for to customer info.
                donation = self._charge_to_donation(
                    charge, self.get_customer(charge.customer)
                )
                donations.append(donation)
            logging.info(f"Stripe - fetched {len(donations)} \
                donations after {self.latest_donation_time}")
            return donations
        except stripe.error.StripeError as e:
            logging.error(
                f"An error occurred while getting new donations: {str(e)}"
            )
            return []  # return an empty list if an error occurs

    def get_customer(self, cus_id: str) -> dict[str, str]:
        """
        Retrieves a customer from Stripe. If cus_id is None,
        it returns a default dict.
        It raises an exception if any StripeError occurs.
        """
        if cus_id is None:
            return {"name": "Unknown", "email": "Unknown"}

        try:
            customer = stripe.Customer.retrieve(cus_id)
            return {"name": customer.name, "email": customer.email}
        except stripe.error.StripeError as e:
            logging.error(
                f"An error occurred while getting a customer: {str(e)}"
            )
            return {"name": "Error", "email": "Error"}

    def _charge_to_donation(self, charge, customer) -> Donation:
        """
        Converts a Stripe charge and customer into a Donation object.
        Uses UTC.
        """
        donor_name = customer.get("name", "Unknown")
        amount = charge.amount / CENTS_IN_DOLLAR if charge.amount else 0.0
        currency = charge.currency if charge.currency else "Unknown"
        email = customer.get("email", "Unknown")
        date_time = charge.created if charge.created else None
        vendor = "Stripe"

        return Donation(
            donor_name, amount, currency, email, date_time, vendor
        )
