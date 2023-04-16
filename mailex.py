import sys
import re
import random
import string
import psycopg2
import uuid
import ssl
import os
import smtplib
from configparser import ConfigParser
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict
#update requirements.txt

def sendmail(data: Dict[str, str]):
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")
    smtp_server = config["smtp"]["server"]
    port_no = config["smtp"]["port"]
    sender_email = config["email"]["sender"]
    sender_password = os.environ['PASSWORD'] #SET ENV VARIABLE OR USE CONFIG.INI config["email"]["password"]
    receiver_email = config["email"]["receiver"]
    
    if "confirmation_number" not in data:
        #if doesnt match with donation mail
        print("Forwarding unknown mail")
        #set mail headers subject
        msg = f"Subject: Unknown Mail Type\n\n{data}"
        
        
    else:
        #match with donation mail
        print("Mailing to donor")
        #sending all mails to the address defined in config.ini for test purposes
        #receiver_email = data["email"] if not "Unknown"
        ack_text = config["msg"]["text"]
        msg = ack_text.format(data)

    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_server, int(port_no), context=context)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg)
    server.quit()
    print("Sent")


def insertdb(data: Dict[str, str]):
    try:
        connection = psycopg2.connect(
          database="test_database",
          user="test_user",
            password="test@123",
            host="127.0.0.1",
            port="5432",
      )
    except:
        print("db connection error");
        sys.exit(1)

    SQL = """
PREPARE SQL (text, text, text, int, text, text, text, text) AS
INSERT INTO netbsd.donation_details VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9);
EXECUTE SQL('{fid}','{contributor}','{curr}','{quantity}','{email}','{vendor}','{datetime}','{amount}','{access_token}');
"""
    try:
        connection.autocommit = False
        cursor = connection.cursor()
        # preparing and inserting data in the database
        #'{fid}','{contributor}','{curr}','{quantity}','{email}','{vendor}','{datetime}','{amount}'
        cursor.execute(
            SQL.format(
                fid=data["confirmation_number"],
                contributor=data["contributor_name"],
                curr=data["currency"],
                quantity=data["quantity"],
                email=data["email"],
                vendor=data["vendor"],
                datetime=data["date_time"],
                amount=data["amount"],
                access_token = data["access_token"]
            )
        )
        cursor.close()
        connection.commit()
        print("Records inserted in the database")
        connection.close()

    except:
        print("Error while inserting. The mail might be unrelated.")



def process_email_content(email_content) -> Dict[str,str]:
    # Remove the email header
    first_html_tag = re.search(r'<html|<!DOCTYPE html', email_content, re.IGNORECASE)
    if first_html_tag:
        email_content = email_content[first_html_tag.start():]
    

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
    details = {}

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
        confirmation_number = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        try:
            contributor_name = contributor_name_match.group(1) if contributor_name_match else "Anonymous"
        except:
            contributor_name = "AttributeError"
        # Print extracted information
        access_token = uuid.uuid4();

        print("Currency:", currency)
        print("Amount:", amount)
        print("Quantity:", quantity)
        print("Email:", email)
        print("Contributor:", contributor_name)
        print("Date and Time:", date_time)
        print("Vendor:", vendor)
        print("Confirmation Number:", confirmation_number)
        print("Access Token:", access_token)

        details["currency"] = currency
        details["amount"] = amount
        details["quantity"] = quantity
        details["email"] = email
        details["contributor_name"] = contributor_name
        details["date_time"] = date_time
        details["vendor"] = vendor
        details["confirmation_number"] = confirmation_number
        details["access_token"] = access_token
        return details

    else:
        print("No payment, donation, or contribution found in the email content")
    return plain_text_content
    


if __name__ == "__main__":
    file_path = sys.argv[1]
    with open(file_path, "r") as file:
        email_content = file.read()
    details = process_email_content(email_content)
    insertdb(details) 
    sendmail(details)
    
    
    
    

