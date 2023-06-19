"""This file contains the Donation class."""
import utils


class Donation:
    """This class represents a donation."""

    def __init__(
        self, donor_name, amount, currency, email, date_time, vendor, quantity=1
    ):
        self.confirmation_number = utils.generate_confirmation_number()
        self.donor_name = donor_name
        self.currency = currency
        self.quantity = quantity
        self.email = email
        self.vendor = vendor
        self.date_time = date_time
        self.amount = amount
        self.access_token = utils.generate_access_token()
