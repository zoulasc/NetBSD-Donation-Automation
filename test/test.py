"""This module sends a test donation. It can used with --stripe 100 or --paypal 100 to send a test donation of $100.00 to the respective payment processor."""

import argparse
import stripe
import logging
import requests
import json


logging.getLogger().addHandler(logging.StreamHandler())


parser = argparse.ArgumentParser(description="Donation Update System.")

parser.add_argument(
    "--stripe",
    nargs="?",
    const="10000",
    default=False,
)

parser.add_argument(
    "--paypal",
    nargs="?",
    const="100",
    default=False,
)

args = parser.parse_args()

if args.stripe:
    stripe.api_key = "sk_test_51NAtgCLWOZAy5SpfukpFqmUparmC3k1fZ0XURnV6o09EdmujE76eQjWtUGdhmOcrIPmVXApu3QACBps8LSy1jtXL00GBTG6CoE"

    logging.info(
        stripe.PaymentIntent.create(
            amount=int(args.stripe) * 100,
            currency="usd",
            payment_method="pm_card_visa",
            confirm=True,
        )
    )
    print(f"sent ${args.stripe} successfully by Stripe")

if args.paypal:
    # PayPal makes me go crazy
    # It takes 3-6 hrs to process a payout

    url = "https://api-m.sandbox.paypal.com/v1/payments/payouts"

    payload = json.dumps(
        {
            "sender_batch_header": {
                "sender_batch_id": "Payouts_1688909706",
                "email_subject": "You have a payout!",
                "email_message": "You have received a payout! Thanks for using our service!",
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {"value": f"{args.paypal}.00", "currency": "USD"},
                    "note": "Thanks for your patronage!",
                    "sender_item_id": "201403140001",
                    "receiver": "sb-4hscv26062116@business.example.com",
                    "notification_language": "en-US",
                }
            ],
        }
    )
    headers = {
        "Content-Type": "application/json",
        "PayPal-Request-Id": "92637a46-0579-4207-995d-fb78643ccbb0",
        "Authorization": "Basic QVVNR1NmODJicFZva0dzbVI1OUNSdTNiTkVwcFRRZUNwWDkydE0tVFlkQnJSampqRmlraWRVdGVsVnVoSkRZQWxfYnlTa19GcG5pRldtWV86RU1vbUE4R21UMk1EMFVpVkF5Uy0yUHN5SDhrWllHeG5jVmJxTGFDdGJWYUwtOGpPX0s3T01qYjRiSjk0WUpUOFZGV0x5Q2NNcldaV3N2ak0=",
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to PayPal API failed: {e}")

    logging.info(response.text)

    print(f"sent ${args.paypal} successfully by PayPal")
