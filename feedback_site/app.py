"""app.py is the main entry point for the feedback site."""
import datetime
import logging
import os
from threading import Thread

from flask import Flask, render_template, request, session

from config import send_thank_mail

from config.utils import allowed_file, valid_uuid
from config.models import Donation, list_to_donation, dict_to_donation

from queries import DonationSQL, FeedbackSQL

from PIL import Image
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.secret_key = "any random string"

# Set up logging
logging.basicConfig(
    filename="website.log",
    level=logging.INFO,
    format="%(levelname)s : %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S%z",
)
logging.getLogger().addHandler(logging.StreamHandler())


def send_async_email(app: Flask, receiver_email: str) -> None:
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
    return render_template("donations.html", year=this_year,donors=Feedback.get_all_by_year(str(this_year)))

@app.route("/validate", methods=["POST"])
def validate() -> str:
    """Validate the provided feedback ID and email."""
    feedback_id = int(request.form.get("feed"))
    email = request.form.get("email")

    # Check if a donation exists for the given email and feedback ID
    donation = DonationSQL.exists_by_email_and_confirmation(email, feedback_id)
    if not donation:
        logging.info(f"No donation found: {email} - {feedback_id}")
        return render_template("nodonation.html")
    logging.info(f"Donation found with: {email} - {feedback_id}")
    
    # Check if feedback already exists for the given feedback ID
    if FeedbackSQL.exists_by_confirmation(feedback_id)[0][0]:
        logging.info(f"Feedback already recieved {email} - {feedback_id}")
        return render_template("invalid.html", identifier=feedback_id)
    
    # Success
    donation = list_to_donation(donation[0])
    session['donation'] = donation.__dict__
    
    logging.info(f"Feedback page created for {donation.confirmation_number}")
    logging.info(f"Validated {email} - {feedback_id}")
    return render_template("valid.html", fid=donation.confirmation_number)


@app.route("/feedback")
def feedback_by_mail():
    """Handle feedback by the url provided via email."""
    token = request.args.get("token")

    # Check if uuid is valid
    if not valid_uuid(token):
        return render_template("nodonation.html")

    # Get confirmation number by uuid
    donation = DonationSQL.exists_by_token(token)

    # Check if a donation exists for the given uuid
    if not donation:
        return render_template("nodonation.html")

    # Check if feedback already exists for the given uuid
    if FeedbackSQL.exists_by_confirmation(donation[0][0])[0][0]:
        logging.info(f"Feedback already recieved {token}")
        return render_template("invalid.html", identifier=confirmation)
    # Success
    donation = list_to_donation(donation[0])
    session['donation'] = donation.__dict__
    
    logging.info(f"Validated {token}")
    logging.info(f"Feedback page created for {donation.confirmation_number}")
    return render_template("valid.html", fid=donation.access_token)


@app.route("/store/<string:token>", methods=["POST"])
def store(token: str) -> str:
    """Store feedback responses and handle optional notification email."""
    
    donation = dict_to_donation(session['donation'])
    
    
    feedback_responses = {
        "confirmation_no": int(donation.confirmation_number),
        "name_question": request.form.get("answer1"),
        "name": request.form.get("name", "Anonymous"),
        "email_question": request.form.get("answer2"),
        "email": request.form.get("email"),
        "notification_question": request.form.get("answer3"),
        "notification_email": request.form.get("notification_email", "-"),
        "logo_filepath": None,
    }
    
    #Get image from the form
    # Save the logo if donation amount exceeds $1000 and image is provided
    amount = float(donation.amount)
    
    if amount > 1000:
        file = request.files.get('logo')
        logging.info(f"Received file: {file.filename}")
        if file and allowed_file(file.filename):
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > 50 * 1024 * 1024:  # 50MB
                logging.error(f"File too large: {file_length}")
                return "File too large", 413  # 413 is HTTP status code for 'Payload Too Large'
            file.seek(0, 0)  # Reset file pointer
            
            filename = secure_filename(donation.access_token + file.filename)
            img = Image.open(file)

            # Determine the new dimensions while keeping the aspect ratio
            aspect_ratio = img.width / img.height
            new_height = new_width = 0
            if amount > 10000:
                new_width = 500
            elif amount > 5000:
                new_width = 350
            else:
                new_width = 150
            new_height = int(new_width / aspect_ratio)  # Calculate new height based on aspect ratio and new width

            # Resizing the image
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
        
            
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
                
            # Save the image file to a directory named 'uploads'
            logging.info(f"Saving file: uploads/{filename}")  
            img.save(f'uploads/{filename}', optimize=True, quality=85)
        
            feedback_responses["logo_filepath"] = f'uploads/{filename}'
    
    logging.info(f"Got feedback {donation.confirmation_number}")
    FeedbackSQL.insert(feedback_responses)
    
    # Send notification email asynchronously to not block the rendering of the thank you page
    Thread(target=send_async_email, args=(app, feedback_responses["notification_email"])).start()

    return render_template("thank_you.html")

