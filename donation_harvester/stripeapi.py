import stripe
from datetime import datetime
from donation import Donation

CENTS_IN_DOLLAR = 100

class StripeAPI:
    def __init__(self, api_key):
        stripe.api_key = api_key

    def get_all_charges(self, limit=5):
        try:
            charges = stripe.Charge.list(limit=limit)
            donations = [self._charge_to_donation(charge) for charge in charges]
            return donations
        except stripe.error.StripeError as e:
            print("An error occurred while getting all charges.")
            # TODO: Log the error details securely.

    def get_charge(self, charge_id):
        try:
            charge = stripe.Charge.retrieve(charge_id)
            customer = self.get_customer(charge.customer)
            return self._charge_to_donation(charge, customer)
        except stripe.error.StripeError as e:
            print("An error occurred while getting a single charge.")
            # TODO: Log the error details securely.

    def get_customer(self, cus_id):
        if cus_id is None:
            return {"name": None, "email": None}

        try:
            customer = stripe.Customer.retrieve(cus_id)
            return {"name": customer.name, "email": customer.email}
        except stripe.error.StripeError as e:
            print("An error occurred while getting the customer.")
            # TODO: Log the error details securely.
            return {"name": None, "email": None}

    def _charge_to_donation(self, charge, customer):
        donor_name = customer["name"]
        amount = charge.amount / CENTS_IN_DOLLAR
        currency = charge.currency
        email = customer["email"]
        date_time = datetime.fromtimestamp(charge.created)
        vendor = "Stripe"

        return Donation(donor_name, amount, currency, email, date_time, vendor)
