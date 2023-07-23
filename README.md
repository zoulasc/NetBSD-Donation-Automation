# NetBSD-Donation-Automation
The project aims to automate the handling of donations.

Continuing the Automation: Automating Donor Acknowledgement and Information Storage & Updating

The project aims to continue and finalize the ongoing work on automating the handling of donations from PayPal and Stripe for NetBSD, ensuring an efficient and streamlined donor experience. It will be done in 350h.

### feedback_site 
is where users send feedbacks by a token or passcode.

### donation_harvester
is where donations are got by apis and stored donor infos

### Installation
To install and run the project, you will need Python 3 and pip installed on your machine. You will also need a PostgreSQL server.

Follow these steps to get the project up and running:

Clone the repository:

```bash
git clone https://github.com/goeksu/NetBSD-Donation-Automation.git
```

Set the database up

```bash
cd config
./set_db.sh -c
```



