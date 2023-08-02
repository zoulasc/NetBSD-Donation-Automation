"""This module handles the file upload and processing."""
import os
import logging
from PIL import Image
from werkzeug.utils import secure_filename
from config.models import Donation

# Set up allowed file extensions for logo
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

IMAGE_LIMIT = 1024 * 1024 # 1MB

AMOUNT_STAGE_1 = 5000 # USD
AMOUNT_STAGE_2 = 10000 # USD

BIG_IMAGE_SIZE_X = 500
BIG_IMAGE_SIZE_Y = 350

SMALL_IMAGE_SIZE_X = 350
SMALL_IMAGE_SIZE_Y = 150

FRONT_PAGE_IMAGE_SIZE_X = 150
FRONT_PAGE_IMAGE_SIZE_Y = 150


def allowed_file(filename):
    """this function checks if the file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def check_size(file):
    """Checks size of file"""
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    logging.info(f"File file_length: {file_length}")
    if file_length > IMAGE_LIMIT:
        logging.error(f"File too large: {file_length}")
        return False
    file.seek(0, 0)  # Reset file pointer
    return True

def calculate_dimensions(max_height, max_width, aspect_ratio):
    """Calculates the dimensions of the image based on the aspect ratio and the max height and width"""
    if aspect_ratio * max_height <= max_width:
        return max_height, int(max_height * aspect_ratio)

    return int(max_width / aspect_ratio), max_width


def prepare_file():
    """Checks if the static folder exists and creates it if it doesn't"""
    if not os.path.exists("static"):
        os.makedirs("static")


def save_file(filename, img):
    """"Save the file to the static folder"""
    path = f"static/{filename}"
    logging.info(f"Saving file: {path}")
    img.save(path, optimize=True)
    return path


def process_file(file, donation) -> str:
    """this function processes the file and returns the path to the file"""
    if not file\
        or not allowed_file(file.filename)\
        or not check_size(file):
        return 429

    prepare_file()

    filename = secure_filename(
        donation.access_token + "." + file.filename.rsplit(".", 1)[-1]
    )

    # name the file with the access token and the file extension
    img = Image.open(file)

    amount = float(donation.amount)

    aspect_ratio = img.width / img.height
    front_page_height = front_page_width = None  # This is for over $10000 donations, logo on front page

    # Calculate the dimensions regarding to donation amount
    if amount <= AMOUNT_STAGE_1:  # 150x350
        new_height, new_width = calculate_dimensions(
            SMALL_IMAGE_SIZE_X, SMALL_IMAGE_SIZE_Y, aspect_ratio
        )

    if amount >= AMOUNT_STAGE_1:  # 350x500
        new_height, new_width = calculate_dimensions(
            BIG_IMAGE_SIZE_X, BIG_IMAGE_SIZE_Y, aspect_ratio
        )

    if amount >= AMOUNT_STAGE_2:  # 150x150 for front page
        front_page_height, front_page_width = calculate_dimensions(
            FRONT_PAGE_IMAGE_SIZE_X, FRONT_PAGE_IMAGE_SIZE_Y, aspect_ratio
        )

    # Resizing the image
    img = img.resize((new_width, new_height), Image.ANTIALIAS)

    if amount >= AMOUNT_STAGE_2:
        img_front = img.resize((front_page_width, front_page_height), Image.ANTIALIAS)
        save_file(f"front-{filename}", img_front)

    return save_file(filename, img)
