import utils


class Donation:
    def __init__(self, donor_name, amount, currency, email, date_time, vendor):
        self.donor_name = donor_name
        self.amount = amount
        self.currency = currency
        self.email = email
        self.date_time = date_time
        self.vendor = vendor
        self.confirmation_number = utils.generate_confirmation_number()
        self.access_token = utils.generate_access_token()
