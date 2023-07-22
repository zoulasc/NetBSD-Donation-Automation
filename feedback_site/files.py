"""This module handles the file upload and processing."""
import os
import logging
from PIL import Image
from werkzeug.utils import secure_filename
from models import Donation

# Set up allowed file extensions for logo
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    """this function checks if the file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_file(file, donation) -> str:
    """this function processes the file and returns the path to the file"""
    if file and allowed_file(file.filename):
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        if file_length > 50 * 1024 * 1024:  # 50MB
            logging.error(f"File too large: {file_length}")
            return (
                "File too large",
                413,
            )  # 413 is HTTP status code for 'Payload Too Large'
        file.seek(0, 0)  # Reset file pointer

        filename = secure_filename(donation.access_token + file.filename)
        img = Image.open(file)

        amount = float(donation.amount)

        # Determine the new dimensions while keeping the aspect ratio
        aspect_ratio = img.width / img.height
        new_height = new_width = 0
        front_page_height = front_page_width = None # This is for over $10000 donations, logo on front page
        if amount >= 10000:
            if int(500 / aspect_ratio) > 350: # 350x500 
                new_height = 350
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = 500
                new_height = int(new_width / aspect_ratio)
                
            if int(150 / aspect_ratio) > 150: # one more 150x150 for front page
                front_page_height = 150
                front_page_width = int(new_height * aspect_ratio)
            else:
                front_page_width = 150
                front_page_height = int(new_width / aspect_ratio)
                
        elif amount >= 5000:
            if int(500 / aspect_ratio) > 350: # 350x500 
                new_height = 350
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = 500
                new_height = int(new_width / aspect_ratio)
        else:
            if int(350 / aspect_ratio) > 350: # 150x350
                new_height = 150
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = 350
                new_height = int(new_width / aspect_ratio)
        
        # Resizing the image
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        if not os.path.exists("static"):
            os.makedirs("static")

        # Save the image file to a directory named 'uploads'
        path = f"static/{filename}"
        logging.info(f"Saving file: {path}")
        img.save(path, optimize=True, quality=85)
        
        if amount >= 10000:
            img_front = img.resize((front_page_width, front_page_height), Image.ANTIALIAS)
            path = f"static/front-{filename}"
            logging.info(f"Saving file: {path}")
            img_front.save(path, optimize=True, quality=85)
        
    return path if path else None
