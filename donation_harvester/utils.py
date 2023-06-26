"""This module is for random stuff."""
import uuid


def generate_confirmation_number() -> str:
    """Generate a random six-digit number"""
    return str(uuid.uuid4().int)[0:6]


def generate_access_token() -> str:
    """Generate a random UUID"""
    return str(uuid.uuid4())
