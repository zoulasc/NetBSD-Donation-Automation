
from typing import Dict, List
import sys
import datetime
from dateutil.parser import parse as parsedate
from bs4 import BeautifulSoup


class HTMLFile:
    baseHTML: str
    spanList: List[str]
    def __init__(self, htmlFile: str) -> None:
        # make parsed html file
        with open(htmlFile) as f:
            self.baseHTML = BeautifulSoup(f, "html.parser")
        # make list of all span tag
        self.spanList = self.baseHTML.find_all("span")

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
    h: HTMLFile

    def __init__(self, h: HTMLFile) -> None:
        self.h = h

    def isDonation(self, span: Dict[str, str]) -> bool:
        return span.string == "Donation Received"

    def getDateTime(self) -> datetime:
        """Get the date from the RFC-2882 header"""
        for i in str(self.h.baseHTML).split("\n"):
            if i.split()[0] == "Date:":
                return parsedate(i[6:])
        return None

    def getEmail(self) -> str:
        for i in self.h.spanList:
            if i.string.split()[0:10] == PAYPAL_TEXT:
                return i.string.split()[-1][1:-2]
        return None

    def getDetails(self) -> Dict[str, str]:
        details = {}
        # XXX: Parse into a dict
        fixme = (str(self.h.baseHTML.find(id="cartDetails").get_text()).strip()).split(
            "\n\n"
        )  # get details(in text) from the tag with id="cartDetails"
        details["fixme"] = fixme
        details["email"] = self.getEmail()
        details["datetime"] = self.getDateTime()
        return details


# class ByStripe(BaseClass):
# EMAIL STRUCTURE UNKNOWN


###Driver Code###
h = HTMLFile(sys.argv[1])
p = ByPayPal(h)
# XXX: put this into a method in PayPal and have that method return the dict or
# none
for _, s in enumerate(h.spanList):
    if p.isDonation(s):
        details = p.getDetails()
        print(details)
        break
