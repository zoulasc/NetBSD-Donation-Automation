import sys
from bs4 import BeautifulSoup

class BaseClass():
    def __init__(self,htmlFile):
        with open(htmlFile) as f:
            self.baseHTML=BeautifulSoup(f,'html.parser')        # make parsed html file
        self.spanList=self.baseHTML.find_all('span')            # make list of all span tag


class ByPaypal(BaseClass):
    def isDonation(self,pos):
        if(self.spanList[pos].string=='Donation Received'):
            return True
        else:
            return False

    def getDate(self):
        for i in str(self.baseHTML).split('\n'):
            if(i.split()[0]=='Date:'):
                return i
            else:
                continue

    def getEmail(self):
        for i in self.spanList:
            if(str(i.string).split()[0:10]==['This', 'email', 'confirms', 'that', 'you', 'have', 'received', 'a', 'donation', 'of']):
                return ("Contributor email: "+(str(i.string).split()[-1])[1:len(str(i.string).split()[-1])-2])
            else:
                continue

    def getDetails(self):
        details=(str(self.baseHTML.find(id="cartDetails").get_text()).strip()).split('\n\n')        # get details(in text) from the tag with id="cartDetails"
        details.append(self.getEmail())
        details.append(self.getDate())
        return details


#class ByStripe(BaseClass):
        #EMAIL STRUCTURE UNKNOWN


###Driver Code###
p=ByPaypal(sys.argv[1])
for i in range(len(p.spanList)):
    if(p.isDonation(i)):
        details=p.getDetails()
        print(details)
        break
    else:
        continue
