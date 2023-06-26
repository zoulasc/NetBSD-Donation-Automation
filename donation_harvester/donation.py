"""
This file contains functions to get new donations from Stripe and Paypal APIs
and organize them
"""

import database

from stripeapi import StripeAPI
from paypalapi import PaypalAPI
from models import Donation


def api_init() -> tuple[StripeAPI, PaypalAPI]:
    """
    Initializes Stripe and Paypal APIs in function when needed to prevent
    delay in the app startup.
    """

    last_donations = database.get_last_donation()

    stripe_api = StripeAPI(
        "sk_test_51NAtgCLWOZAy5SpfukpFqmUparmC3k1fZ0XURnV6o09EdmujE76eQjWt"
        "UGdhmOcrIPmVXApu3QACBps8LSy1jtXL00GBTG6CoE",
        last_donations[0][0],
    )

    paypal_api = PaypalAPI(
        "AUMGSf82bpVokGsmR59CRu3bNEppTQeCpX92tM-TYdBrRjjjFikidUtelVuhJDYAl"
        "_bySk_FpniFWmY_",
        "EMomA8GmT2MD0UiVAyS-2PsyH8kZYGxncVbqLaCtbVaL-8jO_K7OMjb4bJ94YJT8VFWL"
        "yCcMrWZWsvjM",
        last_donations[1][0],
    )
    return stripe_api, paypal_api


def get_new_donations() -> list[Donation]:
    """
    Gets new donations from Stripe and Paypal APIs and returns them in a list
    """

    api = api_init()

    donations = []
    donations += api[0].get_new_donations()  # Stripe API
    donations += api[1].get_new_donations()  # Paypal API

    # Sort donations by date_time in ascending order
    return sorted(donations, key=lambda donation: donation.date_time)


def get_lasts() -> list[Donation]:
    """
    Gets last 10 donations from Stripe and Paypal APIs and returns them in
    a list
    """
    api = api_init()

    donations = []
    donations += api[0].get_all_charges(
        10
    )  # This returns the last 10 charges
    donations += api[1].get_all_charges()[
        :10
    ]  # Paypal does not support limit, goes to 1 month back so
       # sliced for first 10 elements

    return sorted(donations, key=lambda donation: donation.date_time)
