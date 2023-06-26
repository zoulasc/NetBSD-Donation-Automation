"""This is the entry point of the application."""
import sys
from simple_term_menu import TerminalMenu
import mailing
import database
import donation


def main() -> None:
    """Menu for the application."""
    options = ["[c] Check", "[a] See All", "[e] Exit"]
    terminal_menu = TerminalMenu(options, title="Select to proceed:")
    menu_entry_index = terminal_menu.show()
    chosen = menu_entry_index
    if chosen == 0:
        print("> Check...")
        check_last()
    elif chosen == 1:
        print("> See All...")
        see_all()
    elif chosen == 2:
        print("> Exit...")
        sys.exit(1)


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


if __name__ == "__main__":
    main()
