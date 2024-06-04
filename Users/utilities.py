import datetime
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import smtplib

import jwt
from Inbox.msg_emails_Enum import EMAIL_PASSWORD, EMAIL_PORT, EMAIL_SERVER
from Users.models import PasswordResetCode, Users
import re
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def generate_verification_code() -> str:
    """Generate a random 4 digits number for forget password"""
    return ''.join(random.choice('0123456789') for _ in range(4))


def validate_register_data(user_data:dict) -> str:
    """Perform sequential validation checks and return the first error message encountered."""
    
    full_name = user_data.get('user_full_name')
    email = user_data.get('user_email')
    phone = user_data.get('user_phone')
    password = user_data.get('user_password')
    confirm_password = user_data.get('user_password_2')
    
    validators = [
        (lambda value: not check_full_name(value), 'Invalid full name', full_name),
        (lambda value: not check_phone_number(value), 'Invalid phone number', phone),
        (lambda value: not check_valid_password(value), 'Invalid password', password),
        (lambda password: password != confirm_password, "Passwords don't match", password),
        (email_exists, 'Email already exists', email),
        (phone_exists, 'Phone number already exists', phone),
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
    """check if the password is valid, it must contain at least one upper and one lower letter, number and special char"""
    
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'

    return True if re.match(pattern, pas) and len(pas) >= 8 else False


def check_full_name(full_name: str) -> bool:
    '''
    Check if the full name is valid.
    Full name must be at least 4 characters, contain at least one space, and have at least two characters after the space.
    '''
    # Check if full name is at least 4 characters long
    if len(full_name) < 4:
        return False
    
    # Find the first space
    space_index = full_name.find(' ')
    if space_index == -1:
        return False
    
    # Check if there are at least two characters after the space
    if len(full_name[space_index + 1:]) < 2:
        return False
    
    # Check if the part after the space contains only alphabetic characters
    after_space = full_name[space_index + 1:]
    if not after_space.isalpha():
        return False
    
    return True

def check_phone_number(phone_number: str) -> bool:
    '''
    check if the phone number is valid.
    phone number must be at least 10 characters 
    '''
    return len(phone_number) >= 10 and phone_number.isdigit()


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

def set_cookie_in_response(user:Users):
    payload = {
        'user_id': user.user_id,
        'exp': (datetime.datetime.now() + datetime.timedelta(days=30)).timestamp()
    }
    token = jwt.encode(payload, os.getenv('SECRET'), algorithm='HS256')
            
    response = success_response() # return the response
    response.set_cookie(key='Authorization',
                        value=token,
                        httponly=True,
                        samesite='Lax',
                        max_age=30*24*60*60,  # 30 days in seconds
                        expires=(datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%a, %d-%b-%Y %H:%M:%S GMT"))
    
    return response

def validate_change_password_data(request, user:Users) -> str:
    
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    if user.check_password(request.data.get('old_password')) is False:
        return error_response(message="Old password is incorrect", status=400)

    if new_password != new_password_confirm:
        return error_response(message="Passwords don't match.", status=400)

    if check_valid_password(new_password) is False:
        return error_response(message="Password is invalid", status=400)

    return None