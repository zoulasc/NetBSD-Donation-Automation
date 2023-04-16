import sys
import re
import random
import string
from datetime import datetime
from bs4 import BeautifulSoup

def remove_email_header(email_content):
    first_html_tag = re.search(r'<html|<!DOCTYPE html', email_content, re.IGNORECASE)
    if first_html_tag:
        return email_content[first_html_tag.start():]
    return email_content

def generate_random_string():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def process_email_content(email_content):
    # Remove the email header
    email_content = remove_email_header(email_content)

    # Convert HTML content to plain text
    soup = BeautifulSoup(email_content, "html.parser")
    plain_text_content = soup.get_text()

    # Regular expressions to extract information
    payment_pattern = re.compile(r'(?i)(payment|donation|contribution|Money received|payout for )')
    currency_amount_pattern = re.compile(r'([£€$¥₩]\d+(\.\d{2})?)\s*([A-Za-z]{3})?')
    quantity_pattern = re.compile(r'(?i)(quantity):\s*(\d+)')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b(?!\w)')
    vendor_pattern = re.compile(r'(?i)(stripe|paypal)')
    contributor_name_pattern = re.compile(r'(?i)(?:name|contributor|Customer name|from)\s*(\w+\s\w+|\w+)')


    # Extract information
    payment_match = payment_pattern.search(plain_text_content)
    currency_amount_match = currency_amount_pattern.search(plain_text_content)
    quantity_match = quantity_pattern.search(plain_text_content)
    email_match = email_pattern.search(plain_text_content)
    vendor_match = vendor_pattern.search(plain_text_content)
    contributor_name_match = contributor_name_pattern.search(plain_text_content)

    if payment_match:
        amount = float(re.sub(r'[£€$¥₩,]', '', currency_amount_match.group(1)))
        currency = currency_amount_match.group(3) if currency_amount_match.group(3) else "Unknown"
        quantity = int(quantity_match.group(2)) if quantity_match else 1
        try:
            email = email_match.group(0)  if email_match else "Unknown"
        except AttributeError:
            email = "AttributeError"
        date_time = datetime.now()
        vendor = vendor_match.group(1).lower()
        confirmation_number = generate_random_string()
        try:
            contributor_name = contributor_name_match.group(1) if contributor_name_match else "Anonymous"
        except:
            contributor_name = "AttributeError"
        # Print extracted information
        print("Currency:", currency)
        print("Amount:", amount)
        print("Quantity:", quantity)
        print("Email:", email)
        print("Contributor:", contributor_name)
        print("Date and Time:", date_time)
        print("Vendor:", vendor)
        print("Confirmation Number:", confirmation_number)

    else:
        print("No payment, donation, or contribution found in the email content")

if __name__ == "__main__":
    file_path = sys.argv[1]
    with open(file_path, "r") as file:
        email_content = file.read()
    process_email_content(email_content)
