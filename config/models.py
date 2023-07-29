"""This file contains the Donation class."""
from datetime import datetime
from config import utils


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
        self.confirmation_number = utils.generate_confirmation_number() \
            if not confirmation_number else confirmation_number
        self.donor_name = donor_name
        self.currency = currency.upper()
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

def list_to_donation(donation_arr: list[str]) -> Donation:
        return Donation(
            confirmation_number=donation_arr[0],
            donor_name=donation_arr[1],
            currency=donation_arr[2],
            quantity=donation_arr[3],
            email=donation_arr[4],
            vendor=donation_arr[5],
            date_time=donation_arr[6],
            amount=donation_arr[7],
            access_token=donation_arr[8],
        )
        
def dict_to_donation(data: dict[str, str]) -> Donation:
    return Donation(
        donor_name=data.get('donor_name'),
        amount=data.get('amount'),
        currency=data.get('currency'),
        email=data.get('email'),
        date_time=data.get('date_time'),
        vendor=data.get('vendor'),
        confirmation_number=data.get('confirmation_number'),
        access_token=data.get('access_token'),
        quantity=data.get('quantity', 1),
    )
