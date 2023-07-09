"""app.py is the main entry point for the feedback site."""
import logging
from threading import Thread
from uuid import UUID

from flask import Flask, render_template, request
from mailing import sendmail
from models import Donation, Feedback


app = Flask(__name__)

# Set up logging
logging.basicConfig(
    filename="website.log",
    level=logging.INFO,
    format="%(levelname)s : %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S%z",
)
logging.getLogger().addHandler(logging.StreamHandler())


@app.route("/")
def index() -> str:
    """Render the index page."""
    return render_template("index.html")


@app.route("/validate", methods=["POST"])
def validate() -> str:
    """Validate the provided feedback ID and email."""
    feedback_id = int(request.form.get("feed"))
    email = request.form.get("email")

    # Check if a donation exists for the given email and feedback ID
    if not Donation.exists_by_email_and_confirmation(email, feedback_id):
        logging.info(f"No donation found: {email} - {feedback_id}")
        return render_template("nodonation.html")
    logging.info(f"Donation found with: {email} - {feedback_id}")
    
    # Check if feedback already exists for the given feedback ID
    if Feedback.exists_by_confirmation(feedback_id):
        logging.info(f"Feedback already recieved {email} - {feedback_id}")
        return render_template("invalid.html", identifier=feedback_id)
    
    logging.info(f"Validated {email} - {feedback_id}")
    return render_template("valid.html", fid=feedback_id)


@app.route("/feedback")
def feedback_by_mail():
    """Handle feedback provided via email."""
    token = request.args.get("token")

    # Check if uuid is valid
    if not valid_uuid(token):
        return render_template("nodonation.html")

    # Get confirmation number by uuid
    confirmation = Donation.get_by_token(token)

    # Check if a donation exists for the given uuid
    if not confirmation:
        return render_template("nodonation.html")

    # Check if feedback already exists for the given uuid
    if Feedback.exists_by_confirmation(confirmation):
        logging.info(f"Feedback already recieved {token}")
        return render_template("invalid.html", identifier=confirmation)
    logging.info(f"Validated {token}")
    return render_template("valid.html", fid=confirmation)


@app.route("/store/<string:feedback_id>", methods=["POST"])
def store(feedback_id: str) -> str:
    """Store feedback responses and handle optional notification email."""
    feedback_responses = {
        "confirmation_no": int(feedback_id),
        "name_question": request.form.get("answer1"),
        "name": request.form.get("name", "Anonymous"),
        "email_question": request.form.get("answer2"),
        "email": request.form.get("email"),
        "notification_question": request.form.get("answer3"),
        "notification_email": request.form.get("notification_email", "-"),
    }
    logging.info(f"Got feedback {feedback_id}")
    Feedback.insert(feedback_responses)
    # Send notification email asynchronously to not block the rendering of the thank you page
    Thread(target=send_async_email, args=(app, feedback_responses["notification_email"])).start()

    return render_template("thank_you.html")

def send_async_email(app, receiver_email):
    with app.app_context():
        sendmail(receiver_email)

def valid_uuid(uuid_string):
    """Check if the provided string is a valid UUID."""
    try:
        UUID(uuid_string)
        logging.info(f"Valid Token: {uuid_string}")
        return True
    except ValueError:
        logging.info(f"Invalid Token: {uuid_string}")
        return False
