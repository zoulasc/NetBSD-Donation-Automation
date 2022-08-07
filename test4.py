"""parser for extracting details from donation emails"""

# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use

from typing import Dict, List
import sys
import datetime
from dateutil.parser import parse as parsedate
from bs4 import BeautifulSoup


class HTMLFile:
    """for creating parsed html file"""

    base_html: str
    span_list: List[str]

    def __init__(self, html_file: str) -> None:
        with open(html_file, encoding="utf-8") as h_file:
            self.base_html = BeautifulSoup(h_file, "html.parser")
        self.span_list = self.base_html.find_all("span")


PAYPAL_TEXT = [
    "This",
    "email",
    "confirms",
    "that",
    "you",
    "have",
    "received",
    "a",
    "donation",
    "of",
]

STRIPE1_TEXT = "Congratulations netbsd.org!"
STRIPE2_TEXT = "You've just received a payment through Stripe."


class ByPayPal:
    """for donations made by PayPal"""

    html_file: HTMLFile

    def __init__(self, html_file: HTMLFile) -> None:
        self.html_file = html_file

    def get_date_time(self) -> datetime:
        """get the date from the RFC-2882 header"""
        for i in str(self.html_file.base_html).split("\n"):
            words = i.split()
            if words and words[0] == "Date:":
                return parsedate(i[6:]).strftime("%a %d-%m-%Y %I-%M-%S %z %Z")
        return None

    def get_email(self) -> str:
        """get email from the html file"""
        for i in self.html_file.span_list:
            if i.string.split()[0:10] == PAYPAL_TEXT:
                return i.string.split()[-1][1:-2]
        return None

    def get_details(self) -> Dict[str, str]:
        """collect all donor details from the html file"""
        details = {"vendor" : "PayPal"}
        fixme = (
            str(self.html_file.base_html.find(id="cartDetails").get_text()).strip()
        ).split(
            "\n\n\n"
        )  # get details(in text) from the tag with id="cartDetails"
        for i, field in enumerate(fixme):
            fixme[i] = field.split("\n")[-1]
        details["amount"] = fixme[0]
        details["currency"] = fixme[1]
        details["confirmation_no"] = fixme[2]
        details["quantity"] = fixme[3]
        details["contributor"] = fixme[4]
        details["email"] = self.get_email()
        details["datetime"] = self.get_date_time()
        return details

    def is_donation(self, span: Dict[str, str]) -> bool:
        """check if the email is a donation email"""
        return span.string == "Donation Received"

    def analyse_file(self) -> Dict[str, str]:
        """analyse the file for donations made PayPal"""
        for _, string in enumerate(self.html_file.span_list):
            if self.is_donation(string):
                donation_details = self.get_details()
                return donation_details
        return None


class ByStripe:
    """for donations made by Stripe"""

    html_file: HTMLFile

    def __init__(self, html_file: HTMLFile) -> None:
        self.html_file = html_file

    def get_text_details(self, text: List[str]) -> Dict[str, str]:
        """collect all donor details from the text file"""
        details = {"vendor" : "Stripe"}

        def get_field(i: int) -> str:
            return text[i + 1].split()[0]

        for i, line in enumerate(text):
            if line == "-\nPayment":
                details["amount"] = get_field(i)
            if line == "-\nCustomer":
                details["email"] = get_field(i)
            if line == "-\nPayment ID":
                details["confirmation_no"] = text[i + 1]
        return details

    def is_text_donation(self, text: List[str]) -> bool:
        """check if the email is a donation email"""
        for i, line in enumerate(text):
            if line == STRIPE1_TEXT and text[i + 1] == STRIPE2_TEXT:
                return True
        return False

    def analyse_text(self) -> Dict[str, str]:
        """analyse the text file for donations made Stripe"""
        text = str(self.html_file.base_html).split("\n\n")
        if self.is_text_donation(text):
            donation_details = self.get_text_details(text)
            return donation_details
        return None

    def get_html_details(self) -> Dict[str, str]:
        """collect all donor details from the html file"""
        details = {"vendor" : "Stripe"}
        for i in self.html_file.base_html(["style", "script"]):
            i.decompose()
        lst = list((self.html_file.base_html).stripped_strings)
        for i, item in enumerate(lst):
            if item == "Payment":
                details["amount"] = lst[i + 1]
            if item == "Customer":
                details["email"] = lst[i + 1]
            if item == "Payment ID":
                details["confirmation_no"] = lst[i + 1]
        return details

    def is_html_donation(self, span: str) -> bool:
        """check if the email is a donation email"""
        if str(span.string).strip() == STRIPE1_TEXT:
            td_list = self.html_file.base_html.find_all("td")
            for i in td_list:
                if str(i.string).strip() == STRIPE2_TEXT:
                    return True
        return False

    def analyse_html(self) -> Dict[str, str]:
        """analyse the html file for donations made Stripe"""
        for i in self.html_file.span_list:
            if self.is_html_donation(i):
                donation_details = self.get_html_details()
                return donation_details
        return None

    def is_html(self) -> bool:
        """decide whether the file is a html file or not"""
        lst = str(self.html_file.base_html).split()
        for i, item in enumerate(lst):
            if item == "content-type:" and lst[i + 1] == "text/html;":
                return True
        return False

    def analyse_file(self) -> Dict[str, str]:
        """analyse the file's content type and proceed accordingly"""
        if self.is_html():
            return self.analyse_html()
        return self.analyse_text()


###Driver Code###
h = HTMLFile(sys.argv[1])
VENDORS = [ByPayPal, ByStripe]

for vendor in VENDORS:
    processor = vendor(h)
    d = processor.analyse_file()
    if d is not None:
        break

if d is None:
    print(f"{sys.argv[0]}: No vendor matched data for `{sys.argv[1]}'", file=sys.stderr)
    sys.exit(1)
print(d)
