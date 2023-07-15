"""This module sends a test donation. It can used with --stripe 100 or --paypal 100 to send a test donation of $100.00 to the payment processor."""

import argparse
import stripe
import logging
import requests
import json


logging.getLogger().addHandler(logging.StreamHandler())


parser = argparse.ArgumentParser(description="Donation Test")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
    "--stripe",
    nargs="?",
    const="10000",
    default=False,
)

group.add_argument(
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
            customer="cus_OERlOKx1fOyc0a",
            confirm=True,
        )
    )
    print(f"sent ${args.stripe} successfully by Stripe")

if args.paypal:
    # PayPal makes me go crazy
    # It takes 3-6 hrs to process a payout

    url = "https://api-m.sandbox.paypal.com/v1/payments/payouts"

    payload = json.dumps({
    "sender_batch_header": {
        "sender_batch_id": "Payouts_1688915249",
        "email_subject": "You have a payout!",
        "email_message": "You have received a payout! Thanks for using our service!"
    },
    "items": [
        {
        "recipient_type": "EMAIL",
        "amount": {
            "value": f"{args.paypal}.00",
            "currency": "USD"
        },
        "note": "Thanks for your patronage!",
        "sender_item_id": "201403140001",
        "receiver": "sb-4hscv26062116@business.example.com",
        "notification_language": "en-US"
        }
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'PayPal-Request-Id': 'b9a918a8-176f-492a-8f0e-6ac5fdcff91f'
    }





    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to PayPal API failed: {e}")

    logging.info(response.text)

    print(f"sent ${args.paypal} successfully by PayPal")
