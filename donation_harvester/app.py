import donation


all_charges = donation.get_new_donations()
for donation in all_charges:
    print(f"Donor Name: {donation.donor_name}")
    print(f"Amount: {donation.amount}")
    print(f"Currency: {donation.currency}")
    print(f"Date and Time: {donation.date_time}")
    print(f"Email: {donation.email}")
    print(f"Vendor: {donation.vendor}")
    print(f"Confirmation Number: {donation.confirmation_number}")
    print(f"Access Token: {donation.access_token}")
    print("-------------------------------")

print("###")

all_charges = donation.get_last_n(10)
for donation in all_charges:
    print(f"Donor Name: {donation.donor_name}")
    print(f"Amount: {donation.amount}")
    print(f"Currency: {donation.currency}")
    print(f"Date and Time: {donation.date_time}")
    print(f"Email: {donation.email}")
    print(f"Vendor: {donation.vendor}")
    print(f"Confirmation Number: {donation.confirmation_number}")
    print(f"Access Token: {donation.access_token}")
    print("-------------------------------")

print("###")
