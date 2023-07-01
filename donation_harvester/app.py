"""This is the entry point of the application."""
import argparse
import datetime
import json
import logging

from database import get_last_donation_time, insert_donation
from stripeapi import StripeAPI
from paypalapi import PaypalAPI
from mailing import sendmail


def main():
    """
    Main function to orchestrate the operations.
    """
    # Set up logging
    logging.basicConfig(
        filename="donation_harvester.log",
        level=logging.INFO,
        format="%(levelname)s : %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z",
    )
    logging.getLogger().addHandler(logging.StreamHandler())

    # Load credentials. TODO Use environment variables instead
    paypal_client_id = "AUMGSf82bpVokGsmR59CRu3bNEppTQeCpX92tM-TYdBrRjjjFikidUtelVuhJDYAl_bySk_FpniFWmY_"
    paypal_client_secret = "EMomA8GmT2MD0UiVAyS-2PsyH8kZYGxncVbqLaCtbVaL-8jO_K7OMjb4bJ94YJT8VFWLyCcMrWZWsvjM"
    stripe_api_key = "sk_test_51NAtgCLWOZAy5SpfukpFqmUparmC3k1fZ0XURnV6o09EdmujE76eQjWtUGdhmOcrIPmVXApu3QACBps8LSy1jtXL00GBTG6CoE"

    # Fetch the last donation time from the database
    last_donation_time = get_last_donation_time()

    # Parse arguments
    parser = argparse.ArgumentParser(description="Donation Update System.")
    parser.add_argument(
        "--paypal-only", action="store_true", help="Fetches data only from Paypal."
    )
    parser.add_argument(
        "--stripe-only", action="store_true", help="Fetches data only from Stripe."
    )
    parser.add_argument(
        "--json", action="store_true", help="Outputs the results as a JSON file."
    )
    parser.add_argument(
        "--no-email", action="store_true", help="Disables email sending."
    )
    parser.add_argument(
        "--update", action="store_true", help="Enables database insertion."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only prints the actions it would take, without taking them.",
    )

    args = parser.parse_args()
    logging.info(f"Running donation_harvester with args {args}")

    # If no arguments are provided, exit the program.
    if not any(vars(args).values()):
        logging.info("No arguments provided, program is exiting.")
        return

    # Get new donations
    donations = []

    if not args.stripe_only:
        logging.info("Fetching new donations from Paypal...")
        paypal = PaypalAPI(
            paypal_client_id, paypal_client_secret, last_donation_time[1][0]
        )
        donations += paypal.get_new_donations()

    if not args.paypal_only:
        logging.info("Fetching new donations from Stripe...")
        stripe = StripeAPI(stripe_api_key, last_donation_time[0][0])
        donations += stripe.get_new_donations()

    if not donations:
        logging.info("No new donations found.")
        return

    # Output results as a JSON file
    if args.json:
        logging.info("JSON output created.")
        with open("donations.json", "w") as f:
            json.dump(
                [donation.__dict__ for donation in donations],
                f,
                default=lambda x: x.isoformat()
                if isinstance(x, datetime.datetime)
                else x,
            )

    # Insert new donations into the database
    if args.update and not args.dry_run:
        logging.info("Inserting new donations into the database...")
        insert_donation(donations)
    elif args.update and args.dry_run:
        for donation in donations:
            print(
                f"Would insert {donation.email}'s donation of"
                f" {donation.currency} {donation.amount} into database"
            )

    # Send emails
    if not args.no_email and not args.dry_run:
        logging.info("Sending emails...")
        sendmail(donations)


if __name__ == "__main__":
    main()
