"""This module handles the file upload and processing."""
import os
import logging
from config.models import Donation
from PIL import Image
from werkzeug.utils import secure_filename


# Set up allowed file extensions for logo
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

BIG_IMAGE_SIZE_X = 500
BIG_IMAGE_SIZE_Y = 350

SMALL_IMAGE_SIZE_X = 350
BIG_IMAGE_SIZE_Y = 150

FRONT_PAGE_IMAGE_SIZE_X = 150
FRONT_PAGE_IMAGE_SIZE_Y = 150

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

        filename = secure_filename(donation.access_token + "." + file.filename.rsplit('.', 1)[-1]) # name the file with the access token and the file extension
        img = Image.open(file)

        amount = float(donation.amount)

        # Determine the new dimensions while keeping the aspect ratio
        def calculate_dimensions(max_height, max_width, aspect_ratio):
            if aspect_ratio * max_height <= max_width:
                return max_height, int(max_height * aspect_ratio)
            else:
                return int(max_width / aspect_ratio), max_width

        aspect_ratio = img.width / img.height
        front_page_height = front_page_width = None # This is for over $10000 donations, logo on front page

        if amount >= 5000: # 350x500 
            new_height, new_width = calculate_dimensions(BIG_IMAGE_SIZE_X, BIG_IMAGE_SIZE_Y, aspect_ratio)
                
            if amount >= 10000: # 150x150 for front page
                front_page_height, front_page_width = calculate_dimensions(FRONT_PAGE_IMAGE_SIZE_X, FRONT_PAGE_IMAGE_SIZE_Y, aspect_ratio)
                   
        else: # 150x350
            new_height, new_width = calculate_dimensions(SMALL_IMAGE_SIZE_X, SMALL_IMAGE_SIZE_Y, aspect_ratio)

        
        # Resizing the image
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        if not os.path.exists("static"):
            os.makedirs("static")

        # Save the image file to a directory named 'uploads'
        path = f"static/{filename}"
        logging.info(f"Saving file: {path}")
        img.save(path, optimize=True)
        
        if amount >= 10000:
            img_front = img.resize((front_page_width, front_page_height), Image.ANTIALIAS)
            path = f"static/front-{filename}"
            logging.info(f"Saving file: {path}")
            img_front.save(path, optimize=True)
        
    return path if path else None
