import stripeapi

api = stripeapi.StripeAPI(
    "sk_test_51NAtgCLWOZAy5SpfukpFqmUparmC3k1fZ0XURnV6o09EdmujE76eQjWtUGdhmOcrIPmVXApu3QACBps8LSy1jtXL00GBTG6CoE"
)

# Get all charges
all_charges = api.get_all_charges()

# Print all charges


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
