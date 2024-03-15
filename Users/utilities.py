from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import smtplib
from Users.models import Users
import re
import hashlib
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_SERVER = os.environ.get('EMAIL_SERVER')
FROM_EMAIL = os.environ.get('COMPANY_EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

def generate_random_digits() -> str:
    '''Generate a random 4 digits number for forget password'''
    return ''.join(random.choice('0123456789') for _ in range(4))


def send_email(sender_email,receiver_email,message,subject) -> None:
    '''Send an email to the user'''
    try:
        # Create a MIMEMultipart message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Rent Share", sender_email))
        msg["To"] = receiver_email

        part = MIMEText(message,"html")
        msg.attach(part)

        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()
            server.login(sender_email, EMAIL_PASSWORD)
            server.send_message(msg)
    
    except Exception as e:
        logger.error('Error send email: %s', e)
    
    
def check_valid_password(pas:str) -> bool:
    '''check if the password is valid, it must contain at least one upper and one lower letter and number'''

    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)' # contains at least one upper and one lower letter and number.

    return re.match(pattern,pas) and len(pas) >= 8


def hash_password(plain_password:str) -> str:
    '''encrypt the password user using sha256 algorithm'''

    sha256 = hashlib.sha256()
    sha256.update(plain_password.encode('utf-8'))
    hashed_password = sha256.hexdigest()

    return hashed_password


def email_exists(email:str) -> bool:
    '''returns True if user_email already in the db'''
    return Users.objects.filter(user_email=email).exists()


def phone_exists(phone:str)-> bool:
    '''returns True if at least one record matches the filter, and False if no records match.'''
    return Users.objects.filter(user_phone=phone).exists()


def full_name_check(full_name:str) -> bool:
    '''
    check if the full name is valid
    full name must be at least 4 characters and contain at least one space.
    '''
    return len(full_name) >= 4 and full_name.count(' ') >= 1


def phone_number_check(phone_number:str) -> bool:
    '''
    check if the phone number is valid.
    phone number must be at least 10 characters 
    '''
    return len(phone_number) == 10


def check_email_valid(email:str)-> bool:
    '''in registration, the email is checked by Django but when he change it we need to check it again'''
    return email.count('@') == 1 and email.count('.') >= 1