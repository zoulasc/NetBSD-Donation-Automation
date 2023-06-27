"""This is the entry point of the application."""
import sys
import logging
import mailing
import database
import donation


def main() -> None:
    """Menu for the application."""
    n = len(sys.argv)
    if n < 2 or n > 2:
        exit_info()
    command = sys.argv[1]
    if command == "check_lasts":
        check_last()
    elif command == "see_all":
        see_all()
    else:
        exit_info()


def check_last() -> None:
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


def see_all() -> None:
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
    print("Options: check_lasts, see_all")
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
