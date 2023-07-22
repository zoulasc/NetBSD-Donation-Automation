"""This file contains the Donation class."""
from datetime import datetime


class Donation:
    """This class represents a donation."""

    def __init__(
        self,
        donor_name: str,
        amount: float,
        currency: str,
        email: str,
        date_time: int,
        vendor: str,
        confirmation_number=None,
        access_token=None,
        quantity: int = 1,
    ) -> None:
        self.confirmation_number = confirmation_number
        self.donor_name = donor_name
        self.currency = currency
        self.quantity = quantity
        self.email = email
        self.vendor = vendor
        self.date_time = date_time
        self.amount = amount
        self.access_token = access_token
