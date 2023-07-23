"""This is the entry point of the application."""
import argparse
from datetime import datetime
import logging
from typing import List, Dict

from database import get_last_donation_time, \
    get_donations_in_range, insert_donation, \
    get_deferred_emails, delete_deferred_emails, \
    insert_deferred_email
from stripeapi import StripeAPI
from paypalapi import PaypalAPI
from config import send_url_mail
from config.utils import json_output

def main():
    """
    Main function to orchestrate the operations regarding to arguments given.
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

    # Parse arguments
    parser = argparse.ArgumentParser(description="Donation Update System.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    update_parser = subparsers.add_parser('update', help="Enables database insertion.")
    update_parser.add_argument("--paypal-only", action="store_true", \
        help="Fetches data only from Paypal.")
    update_parser.add_argument("--stripe-only", action="store_true", \
        help="Fetches data only from Stripe.")
    update_parser.add_argument("--dry-run", action="store_true", \
        help="Only prints the actions it would take, without taking them.")
    update_parser.add_argument("--no-email", action="store_true", help="Disables email sending.")
    update_parser.add_argument("--json", nargs='?', const='donations.json', \
        help="Outputs the results as a JSON file. You can optionally specify the output file name.")

    list_parser = subparsers.add_parser('list', help="Lists the donations from the database.")
    list_parser.add_argument("--paypal-only", action="store_true", \
        help="Fetches data only from Paypal.")
    list_parser.add_argument("--stripe-only", action="store_true", \
        help="Fetches data only from Stripe.")
    list_parser.add_argument("--begin-date", type=lambda s: int(datetime.strptime(s, "%Y-%m-%d")\
        .timestamp()), help="The begin date for listing donations (format: YYYY-MM-DD).")
    list_parser.add_argument("--end-date", type=lambda s: int(datetime.strptime(s, "%Y-%m-%d")\
        .timestamp()), help="The end date for listing donations (format: YYYY-MM-DD).")
    list_parser.add_argument("--json", nargs='?', const='donations.json', \
        help="Outputs the results as a JSON file. You can optionally specify the output file name.")

    send_parser = subparsers.add_parser('send-deferred-emails', help="Send deferred emails.")


    args = parser.parse_args()
    logging.info(f"---RUNNING donation_harvester--- \n args: {args}")

    # Get new donations
    donations = []

    if args.command == "update":
        # Fetch the last donation time from the database
        last_donation_time = get_last_donation_time()
        # Fetch new donations from PayPal
        if not args.stripe_only:
            logging.info("Fetching new donations from Paypal...")
            paypal = PaypalAPI(
                paypal_client_id, paypal_client_secret, last_donation_time[0][0]
            )
            donations += paypal.get_new_donations()

        # Fetch new donations from Stripe
        if not args.paypal_only:
            logging.info("Fetching new donations from Stripe...")
            stripe = StripeAPI(stripe_api_key, last_donation_time[1][0])
            donations += stripe.get_new_donations()

        if not donations:
            logging.info("No new donations found.")
            return

        # Insert new donations into the database
        if not args.dry_run:
            logging.info("Inserting new donations into the database...")
            insert_donation(donations)
        else:
            # Dry-run
            for donation in donations:
                print(
                    f"Would insert and send mail to {donation.email}\
                        for the donation in {donation.date_time}"
                )
            print(f"Would insert {len(donations)} donations in total.")

        # Send emails
        if not args.no_email and not args.dry_run:
            logging.info("Sending emails...")
            sendmail(donations)

        if args.json:
            json_output(donations, args.json)

    elif args.command == "list":
        end_date = args.end_date or int(datetime.now().timestamp())
        # get current timestamp if not provided
        begin_date = args.begin_date or (end_date - 2419200)
        # get timestamp from 1 month ago if not provided

        if args.stripe_only:
            vendor = ("Stripe",)
        elif args.paypal_only:
            vendor = ("PayPal",)
        else:
            vendor = None

        donations = get_donations_in_range(begin_date, end_date, vendor)
        for donation in donations:
            donation.print_donation()
        if args.json:
            json_output(donations, args.json)

    elif args.command == "send-deferred-emails":
        logging.info("Checking for deferred emails...")
        donations = get_deferred_emails()
        if not donations:
            logging.info("No deferred emails found.")
        else:
            print(f"Are you sure you want to send {len(donations)} deferred emails? (y/n)")
            if input() == "y":
                delete_deferred_emails()
                sendmail(donations)
     # If runned without required arguments
    else:
        logging.info("No required arguments provided, program is exiting.")
        
def sendmail(donations):
    """
    This function send mails to the donors, and insert the failed ones into the database.
    """
    deferred = send_url_mail(donations)
    if deferred:
        logging.info("Inserting deferred emails into the database...")
        insert_deferred_email(deferred)

if __name__ == "__main__":
    main()
