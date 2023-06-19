"""This is the entry point of the application."""
import sys
import mailing
import database
import donation

if sys.argv[1] == "check":
    donations = donation.get_new_donations()
    if len(donations) == 0:
        print("No new donations")
        sys.exit()
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

if sys.argv[1] == "all":
    all_charges = donation.get_lasts()
    for donation_ in all_charges:
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
