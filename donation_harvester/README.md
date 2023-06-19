# Project: NetBSD Donation Automation - Donation Harvester

This project automates the process of getting and storing the donations.

### Description
The doantion harvester system is a python application that collects donations from Stripe and PayPal api and stores it in a PostgreSQL database. 

### Installation
To install and run the project, you will need Python 3 and pip installed on your machine. You will also need a PostgreSQL server to store the feedback data.

Follow these steps to get the project up and running:

Clone the repository:

```bash
git clone https://github.com/goeksu/NetBSD-Donation-Automation.git
cd NetBSD-Donation-Automation/donation_harvester
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Set up your PostgreSQL server and replace the database connection parameters in the database.py file with your own parameters.
Run the Flask application:

```bash
python app.py
```

## Files
app.py - main entry point to the app. checks for args.<br>
models - holds donation class<br>
donation - gets data from apis and organizes them.<br>
paypalapi- connections to paypal<br>
stripeapi- connections to stripe<br>
database- database connections<br>
mailing- mailing stuff<br>
utils - generates uuids and numbers

## For Database
```SQL
CREATE USER test_user WITH PASSWORD 'test@123';
ALTER USER test_user WITH SUPERUSER;


CREATE DATABASE test_database
  WITH TEMPLATE = template0
       OWNER = test_user
        ENCODING = 'UTF8';


\c test_database 


CREATE SCHEMA "netbsd"
  AUTHORIZATION test_user;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE netbsd.donation_details
(
  confirmation_no character varying NOT NULL,
  contributor character varying,
  currency character varying,
  quantity integer,
  email character varying NOT NULL,
  vendor character varying NOT NULL,
  datetime character varying,
  access_token UUID NOT NULL DEFAULT gen_random_uuid(),
  CONSTRAINT donation_details_pkey PRIMARY KEY (confirmation_no)
);
ALTER TABLE netbsd.donation_details
  OWNER TO test_user;


CREATE TABLE netbsd.feedbacks
(
  confirmation_no character varying NOT NULL,
  answer1 boolean NOT NULL,
  name character varying,
  answer2 boolean NOT NULL,
  email character varying,
  answer3 boolean NOT NULL,
  notificationi_email character varying,
  CONSTRAINT payment_id PRIMARY KEY (confirmation_no)
);
ALTER TABLE netbsd.feedbacks
  OWNER TO test_user;
```
