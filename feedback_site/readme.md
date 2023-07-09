# Project: NetBSD Donation Automation - Feedback Site

This project automates the process of collecting and storing feedback from donors in the NetBSD project.

### Description
The NetBSD Donation Automation system is a Flask web application that collects donor feedback and stores it in a PostgreSQL database. The application provides endpoints for the frontend to send feedback data and for the backend to store the feedback data.

### Installation
To install and run the project, you will need Python 3 and pip installed on your machine. You will also need a PostgreSQL server to store the feedback data.

Follow these steps to get the project up and running:

Clone the repository:

```bash
git clone https://github.com/goeksu/NetBSD-Donation-Automation.git
cd NetBSD-Donation-Automation/feedback_site
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Set up your PostgreSQL server and replace the database connection parameters in the database.py file with your own parameters.
Run the Flask application:

```bash
flask run
```

The application will start running at http://localhost:5000.
Usage
Once the application is running, you can navigate to http://localhost:5000 in your web browser to view the application.

