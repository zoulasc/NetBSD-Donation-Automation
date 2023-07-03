"""This module is for random stuff."""
import uuid
import logging
import json


def generate_confirmation_number() -> str:
    """Generate a random six-digit number"""
    return str(uuid.uuid4().int)[0:6]


def generate_access_token() -> str:
    """Generate a random UUID"""
    return str(uuid.uuid4())

def json_output(donations, filename='donations.json') -> None:
    """Output results as a JSON file"""
    with open(filename, 'w') as f:
        json.dump(
            [donation.__dict__ for donation in donations],f
            )
    logging.info(f"Successfully outputted results as {filename}")
