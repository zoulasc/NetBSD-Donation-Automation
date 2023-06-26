"""This file contains the Donation class."""
import utils

from datetime import datetime


class Donation:
    """This class represents a donation."""

    def __init__(
        self,
        donor_name: str,
        amount: float,
        currency: str,
        email: str,
        date_time: datetime,
        vendor: str,
        quantity: int = 1,
    ) -> None:
        self.confirmation_number = utils.generate_confirmation_number()
        self.donor_name = donor_name
        self.currency = currency
        self.quantity = quantity
        self.email = email
        self.vendor = vendor
        self.date_time = date_time
        self.amount = amount
        self.access_token = utils.generate_access_token()
