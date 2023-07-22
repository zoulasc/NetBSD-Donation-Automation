"""This file contains the Donation class."""
from datetime import datetime
from typing import List, Dict
import utils


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
        confirmation_number = None,
        access_token = None,
        quantity: int = 1,
    ) -> None:
        self.confirmation_number = utils.generate_confirmation_number() \
            if not confirmation_number else confirmation_number
        self.donor_name = donor_name
        self.currency = currency
        self.quantity = quantity
        self.email = email
        self.vendor = vendor
        self.date_time = date_time
        self.amount = amount
        self.access_token = utils.generate_access_token() if not access_token else access_token
    def print_donation(self) -> None:
        """Print donation details."""
        print(
            f" name: {self.donor_name}\n",
            f"email: {self.email}\n",
            f"amount: {self.amount}\n",
            f"currency: {self.currency}\n",
            f"date_time: {datetime.fromtimestamp(self.date_time)}\n", # prints in readable format
            f"vendor: {self.vendor}\n",
            f"confirmation_number: {self.confirmation_number}\n",
            f"access_token: {self.access_token}\n",
            "----------------------------------------"
        )

def donation_to_dict(donations: List[Donation]) -> List[Dict]:
    if not donations:
        return None
    donations_dict = []
    for donation in donations:
        donations_dict.append({
            "confirmation_number": donation.confirmation_number,
            "donor_name": donation.donor_name,
            "currency": donation.currency,
            "quantity": donation.quantity,
            "email": donation.email,
            "vendor": donation.vendor,
            "date_time": donation.date_time,
            "amount": donation.amount,
            "access_token": donation.access_token,
        })
    return donations_dict

def dict_to_donation(donations_dict: List[Dict]) -> List[Donation]:
    if not donations_dict:
        return None
    donations = []
    for donation_dict in donations_dict:
        donations.append(Donation(
            confirmation_number=donation_dict.get("confirmation_number"),
            donor_name=donation_dict.get("donor_name"),
            currency=donation_dict.get("currency"),
            quantity=donation_dict.get("quantity"),
            email=donation_dict.get("email"),
            vendor=donation_dict.get("vendor"),
            date_time=donation_dict.get("date_time"),
            amount=donation_dict.get("amount"),
            access_token=donation_dict.get("access_token"),
        ))
    return donations