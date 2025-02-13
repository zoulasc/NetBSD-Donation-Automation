"""This module is for random stuff."""
import uuid
import logging
import json

# Set up allowed file extensions for logo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def generate_confirmation_number() -> str:
    """Generate a random six-digit number"""
    return str(uuid.uuid4().int)[0:10]

def generate_access_token() -> str:
    """Generate a random UUID"""
    return str(uuid.uuid4())

def json_output(donations, filename: str='donations.json') -> None:
    """Output results as a JSON file"""
    with open(filename, 'w') as f:
        json.dump(
            [donation.__dict__ for donation in donations],f
            )
    logging.info(f"Successfully outputted results as {filename}")
    
def check_length(string:str) -> bool:
    """Check if the length of the string is less than 50"""
    return len(string) < 50

def valid_uuid(uuid_string: str) -> bool:
    """Check if the provided string is a valid UUID."""
    try:
        uuid.UUID(uuid_string)
        logging.info(f"Valid Token: {uuid_string}")
        return True
    except ValueError:
        logging.info(f"Invalid Token: {uuid_string}")
        return False
