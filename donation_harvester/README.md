# Project: NetBSD Donation Automation - Donation Harvester

This project automates the process of getting and storing the donations.

### Description
The doantion harvester system is a python application that collects donations from Stripe and PayPal api and stores it in a PostgreSQL database. 

### Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Set up your PostgreSQL server and replace the database connection parameters in the database.py file with your own parameters.
Run the Flask application:

```bash
python app.py [args]

Donation Update System.

positional arguments:
  {update,list,send-deferred-emails}
    update              Enables database insertion.
    list                Lists the donations from the database.
    send-deferred-emails
                        Send deferred emails.

options:
  -h, --help            show this help message and exit

```


