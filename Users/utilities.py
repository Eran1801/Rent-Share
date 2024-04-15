from django.contrib.auth.hashers import make_password
from Users.utilities import check_full_name, email_exists, phone_exists, check_valid_password, check_phone_number
from Users.utilities import check_email_valid, email_exists, check_full_name, phone_exists, check_phone_number
from django.http import JsonResponse
from django.utils import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import smtplib
from Users.models import PasswordResetCode, Users
import re
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_SERVER = os.environ.get('EMAIL_SERVER')
FROM_EMAIL = os.environ.get('COMPANY_EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')


def generate_verification_code() -> str:
    """Generate a random 4 digits number for forget password"""
    return ''.join(random.choice('0123456789') for _ in range(4))


def validate_register_data(user_data:dict) -> str:
    """Perform sequential validation checks and return the first error message encountered."""
    validators = [
        (lambda value: not check_full_name(value), 'Invalid full name', user_data.get('user_full_name')),
        (email_exists, 'Email already exists', user_data.get('user_email')),
        (phone_exists, 'Phone number already exists', user_data.get('user_phone')),
        (lambda value: not check_phone_number(value), 'Invalid phone number', user_data.get('user_phone')),
        (lambda value: not check_valid_password(value), 'Invalid password', user_data.get('user_password')),
        (lambda password: password != user_data.get('user_password_2'), "Passwords don't match",
         user_data.get('user_password')),
    ]

    for validator, error_msg, value in validators:
        if validator(value):
            return error_msg  # Return the error message if the validator condition is met
    return None  # No errors found


def validate_update_user_info(user:Users, full_name:str, email:str, phone:str) -> str:
    """Update user information and perform validation"""
    
    # Check if full name needs to be updated
    if full_name != user.user_full_name:
        if check_full_name(full_name) is False:
            return "Invalid full name"
        else:
            user.user_full_name = full_name  # Update full name in the database

    # Check if email needs to be updated
    if email != user.user_email:
        if email_exists(email):
            return "Email already exists"
        elif check_email_valid(email) is False:
            return "Email is invalid"
        else:
            user.user_email = email  # Update email in the database

    # Check if phone number needs to be updated
    if phone != user.user_phone:
        if phone_exists(phone):
            return "Phone number already exists"
        elif check_phone_number(phone) is False:
            return "Phone number is invalid"
        else:
            user.user_phone = phone  # Update phone number in the database
    
    return "success"


def send_email(sender_email:str, receiver_email:str, message:str, subject:str) -> None:
    """Email the user"""
    try:
        # Create a MIMEMultipart message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Rent Share", sender_email))
        msg["To"] = receiver_email

        part = MIMEText(message, "html")
        msg.attach(part)

        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()
            server.login(sender_email, EMAIL_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        logger.error('Error send email: %s', e)


def email_exists(email: str) -> bool:
    '''returns True if user_email already in the db'''
    return Users.objects.filter(user_email=email).exists()


def phone_exists(phone: str) -> bool:
    '''returns True if at least one record matches the filter, and False if no records match.'''
    return Users.objects.filter(user_phone=phone).exists()


def check_valid_password(pas: str) -> bool:
    """check if the password is valid, it must contain at least one upper and one lower letter and number"""

    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)'  # contains at least one upper and one lower letter and number.

    return True if re.match(pattern, pas) and len(pas) >= 8 else False


def check_full_name(full_name: str) -> bool:
    '''
    check if the full name is valid
    full name must be at least 4 characters and contain at least one space.
    '''
    return len(full_name) >= 4 and full_name.count(' ') >= 1


def check_phone_number(phone_number: str) -> bool:
    '''
    check if the phone number is valid.
    phone number must be at least 10 characters 
    '''
    return len(phone_number) >= 10


def check_email_valid(email: str) -> bool:
    '''in registration, the email is checked by Django but when he change it we need to check it again'''
    return email.count('@') == 1 and email.count('.') >= 1


def check_verification_code_expiry(verification_code:str,object:PasswordResetCode) -> bool:
    """This function will check if the verification code is expired or not"""
    
    # Calculate the current time
    current_time = timezone.now()
    # Calculate the time 5 minutes ago
    expiry_time = object.created_at + timezone.timedelta(minutes=5) 
    
    return current_time > expiry_time


def encrypt_password(plain_password: str) -> str:
    '''encrypt the password user using PBKDF2 algorithm'''
    
    return make_password(plain_password)


def success_response(data:dict=None, message="Success", status=200) -> JsonResponse:
    """
    Helper function to generate success response.
    """
    response_data = {'data': data, 'message': message}
    return JsonResponse(response_data, status=status)


def error_response(message="Error", status=400) -> JsonResponse:
    """
    Helper function to generate error response.
    """
    response_data = {'error': message}
    return JsonResponse(response_data, status=status)