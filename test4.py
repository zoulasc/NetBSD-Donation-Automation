"""parser for extracting details from donation emails"""
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


class ByPayPal:
    """for donations made by PayPal"""

    html_file: HTMLFile

    def __init__(self, html_file: HTMLFile) -> None:
        self.html_file = html_file

    def get_date_time(self) -> datetime:
        """get the date from the RFC-2882 header"""
        for i in str(self.html_file.base_html).split("\n"):
            if i.split()[0] == "Date:":
                return parsedate(i[6:])
        return None

    def get_email(self) -> str:
        """get email from the html file"""
        for i in self.html_file.span_list:
            if i.string.split()[0:10] == PAYPAL_TEXT:
                return i.string.split()[-1][1:-2]
        return None

    def get_details(self) -> Dict[str, str]:
        """collect all donor details from the html file"""
        details = {}
        fixme = (
            str(self.html_file.base_html.find(id="cartDetails").get_text()).strip()
        ).split(
            "\n\n\n"
        )  # get details(in text) from the tag with id="cartDetails"
        for i in fixme:
            fixme[fixme.index(i)] = i.split("\n")[-1]
        details["amount"] = fixme[0]
        details["currency"] = fixme[1]
        details["confirmation_no."] = fixme[2]
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
        details = {}
        for line in text:
            if line == "-\nPayment":
                details["amount"] = (text[(text.index(line)) + 1]).split()[0]
            if line == "-\nCustomer":
                details["customer"] = (text[(text.index(line)) + 1]).split()[0]
            if line == "-\nPayment ID":
                details["payment_id"] = text[(text.index(line)) + 1]
        return details

    def is_text_donation(self, text: List[str]) -> bool:
        """check if the email is a donation email"""
        for line in text:
            if (
                line == "Congratulations netbsd.org!"
                and text[(text.index(line)) + 1]
                == "You've just received a payment through Stripe."
            ):
                return True
        return None

    def analyse_text(self) -> Dict[str, str]:
        """analyse the text file for donations made Stripe"""
        text = str(self.html_file.base_html).split("\n\n")
        if self.is_text_donation(text):
            donation_details = self.get_text_details(text)
            return donation_details
        return None

    def get_html_details(self) -> Dict[str, str]:
        """collect all donor details from the html file"""
        details = {}
        for i in self.html_file.base_html(["style", "script"]):
            i.decompose()
        lst = list((self.html_file.base_html).stripped_strings)
        for i in lst:
            if i == "Payment":
                details["amount"] = lst[(lst.index(i)) + 1]
            if i == "Customer":
                details["customer"] = lst[(lst.index(i)) + 1]
            if i == "Payment ID":
                details["payment_id"] = lst[(lst.index(i)) + 1]
        return details

    def is_html_donation(self, span: str) -> bool:
        """check if the email is a donation email"""
        if str(span.string).strip() == "Congratulations netbsd.org!":
            td_list = self.html_file.base_html.find_all("td")
            for i in td_list:
                if (
                    str(i.string).strip()
                    == "You've just received a payment through Stripe."
                ):
                    return True
        return None

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
        for i in lst:
            if i == "content-type:" and lst[(lst.index(i)) + 1] == "text/html;":
                return True
        return None

    def analyse_file(self) -> Dict[str, str]:
        """analyse the file's content type and proceed accordingly"""
        if self.is_html():
            return self.analyse_html()
        return self.analyse_text()


###Driver Code###
h = HTMLFile(sys.argv[1])
p = ByPayPal(h)
print(p.analyse_file())
s = ByStripe(h)
print(s.analyse_file())
