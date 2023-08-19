"""app.py is the main entry point for the feedback site."""
from configparser import ConfigParser
import datetime
import logging
from threading import Thread

from flask import Flask, render_template, request, session
from flask_talisman import Talisman


from config import send_thank_mail

from config.utils import valid_uuid, check_length
from config.models import Donation, list_to_donation, dict_to_donation

from files import process_file
from queries import DonationSQL, FeedbackSQL

csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'style-src': '\'self\''
}

app = Flask(__name__)
Talisman(app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
    force_https=False) # TODO for development only

config = ConfigParser()
config.read("config/config.ini", encoding="utf-8")

# Set up session
app.secret_key = config["website"]["secret_key"] 
app.config.update(
    SESSION_COOKIE_SAMESITE='Strict'
)

AMOUNT_LOGO_LIMIT = 1000 # USD


# Set up logging
logging.basicConfig(
    filename="website.log",
    level=logging.INFO,
    format="%(levelname)s : %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S%z",
)
logging.getLogger().addHandler(logging.StreamHandler())


def send_async_email(app: Flask, receiver_email: str) -> None:
    """Send asynchronous thank you email while not to block the rendering of the thank you page"""
    with app.app_context():
        send_thank_mail(receiver_email)

@app.route("/")
def index() -> str:
    """Render the index page."""
    return render_template("index.html")


@app.route("/donations")
def donations() -> str:
    """Render the index page."""
    this_year = datetime.datetime.now().year
    return render_template(
        "donations.html",
        year=this_year,
        donors=FeedbackSQL.get_all_by_year(str(this_year)),
    )


@app.route("/validate", methods=["POST"])
def validate() -> str:
    """Validate the provided feedback ID and email."""
    feedback_id = request.form.get("feed")
    email = request.form.get("email")
    
    if not check_length(feedback_id) or not check_length(email):
        logging.info(f"Invalid length: {email} - {feedback_id}")
        return render_template("index.html",error= -1)

    # Check if a donation exists for the given email and feedback ID
    donation = DonationSQL.exists_by_email_and_confirmation(email, feedback_id)
    if not donation:
        logging.info(f"No donation found with related info.")
        return render_template("index.html",error= -1)
    logging.info(f"Donation found with: {email} - {feedback_id}")

    # Check if feedback already exists for the given feedback ID
    if FeedbackSQL.exists_by_confirmation(feedback_id)[0][0]:
        logging.info(f"Feedback already recieved {email} - {feedback_id}")
        return render_template("index.html", error=feedback_id)

    # Success
    donation = list_to_donation(donation[0])
    session['donation'] = donation.__dict__
    logging.info(f"Feedback page created for {donation.confirmation_number}")
    logging.info(f"Validated {email} - {feedback_id}")
    return render_template("valid.html", fid=donation.access_token, amount=float(donation.amount))


@app.route("/feedback")
def feedback_by_mail() -> str:
    """Handle feedback by the url provided via email."""
    token = request.args.get("token")

    # Check if uuid is valid
    if not valid_uuid(token):
        return render_template("index.html",error= -1)

    # Get confirmation number by uuid
    donation = DonationSQL.exists_by_token(token)

    # Check if a donation exists for the given uuid
    if not donation:
        return render_template("index.html",identifier= -1)
    # Check if feedback already exists for the given uuid
    confirmation_no = donation[0][0]
    if FeedbackSQL.exists_by_confirmation(confirmation_no)[0][0]:
        logging.info(f"Feedback already recieved {token}")
        return render_template("index.html", error=confirmation_no)
    # Success
    donation = list_to_donation(donation[0])
    session['donation'] = donation.__dict__
    logging.info(f"Validated {token}")
    logging.info(f"Feedback page created for {donation.confirmation_number}")
    return render_template("valid.html", fid=donation.access_token, amount=float(donation.amount))


@app.route("/store/<string:token>", methods=["POST"])
def store(token) -> str:
    """Store feedback responses and handle optional notification email."""

    donation = dict_to_donation(session["donation"])

    feedback_responses = {
        "confirmation_no": int(donation.confirmation_number),
        "name_question": request.form.get("answer_name"),
        "name": request.form.get("name", "Anonymous"),
        "email_question": request.form.get("answer_email"),
        "email": request.form.get("email"),
        "notification_question": request.form.get("answer_notification_email"),
        "notification_email": request.form.get("notification_email", "-"),
        "logo_filepath": request.form.get("logo", None),
    }
    
    for key, value in feedback_responses.items():
        if key.endswith("confirmation_no") or not value:
            continue
        if not check_length(value):
            logging.info(f"Invalid length.")
            return render_template("valid.html",
                                       fid=donation.access_token,
                                       amount=float(donation.amount),
                                       error="Response too long")

    # Get image from the form
    # Save the logo if donation amount exceeds $1000 and image is provided

    if float(donation.amount) >= AMOUNT_LOGO_LIMIT:
        file = request.files.get("logo")
        if file:
            logging.info(f"Received file: {file.filename}")
            path = process_file(file, donation)
            if path == 429: # File too large
                logging.error("Error related to image attached")
                return render_template("valid.html",
                                       fid=donation.access_token,
                                       amount=float(donation.amount),
                                       error="File too large")
            feedback_responses["logo_filepath"] = path
        else:
            logging.info("No file received")
            feedback_responses["logo_filepath"] = "Empty"

    logging.info(f"Got feedback {donation.confirmation_number}")
    FeedbackSQL.insert(feedback_responses)

    # Send notification email asynchronously to not block the rendering of the thank you page
    Thread(
        target=send_async_email, args=(app, feedback_responses["notification_email"])
    ).start()

    return render_template("thank_you.html")
