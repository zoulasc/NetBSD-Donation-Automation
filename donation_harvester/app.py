"""This is the entry point of the application."""
import sys
import logging
import mailing
import database
import donation

"""TODO
    *-dry-run,
    *-update,
    date selection,
    paypal-only,
    stripe-only,
    list 5(from database, get an int and return lines as much as the given number),
    json
    no-email
"""


def main() -> None:
    """CLi handler for the application."""
    global commandDict
    commandDict = {"--update": updateDonations, "--dry-run": dryRun}

    if len(sys.argv) < 2:
        exit_info()

    commandline_args = sys.argv[1:]

    for argument in commandline_args:
        if argument in commandDict:
            commandDict[argument]()
        else:
            exit_info()


def updateDonations() -> None:
    """Checks for new donations and sends them to database and mailing functions."""
    donations = donation.get_new_donations()
    if not donations:
        print("No new donations")
        sys.exit(1)

    for donation_ in donations:
        print(f"Donor Name: {donation_.donor_name}")
        print(f"Amount: {donation_.amount}")
        print(f"Currency: {donation_.currency}")
        print(f"Date and Time: {donation_.date_time}")
        print(f"Email: {donation_.email}")
        print(f"Vendor: {donation_.vendor}")
        print(f"Confirmation Number: {donation_.confirmation_number}")
        print(f"Access Token: {donation_.access_token}")
        print("-------------------------------")
    print("###")

    database.insert_donation(donations)
    mailing.sendmail(donations)


def dryRun() -> None:
    """Shows last donations from API."""
    all_charges = donation.get_lasts()
    for donation_ in all_charges:
        print(f"Donor Name: {donation_.donor_name}")
        print(f"Amount: {donation_.amount}")
        print(f"Currency: {donation_.currency}")
        print(f"Date and Time: {donation_.date_time}")
        print(f"Email: {donation_.email}")
        print(f"Vendor: {donation_.vendor}")
        print("-------------------------------")
    print("###")


def exit_info() -> None:
    """Shows exit information."""
    print("Usage: python app.py <option>")
    print("Options:", end=" ")
    for keys in commandDict.keys():
        print(keys, end=" ")
    print()
    sys.exit(1)


if __name__ == "__main__":
    """Start application and configure logging."""
    logging.basicConfig(
        filename="donation_harvester.log",
        level=logging.INFO,
        format="%(levelname)s : %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z",
    )
    logging.info("Running donation_harvester")

    main()
