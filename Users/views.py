from email.utils import formataddr
import random
import smtplib
from django.db import connection
from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from django.http import *
from rest_framework.decorators import api_view
from Posts.views import convert_base64_to_image
from Users.models import Users
from Users.serializers import UsersSerializer
import re
import hashlib
import logging
from validate_email import validate_email
from email.message import EmailMessage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PORT = 587
EMAIL_SERVER = "smtp-mail.outlook.com"  # Adjust server address, if you are not using @outlook
FROM_EMAIL = "rentbuzz@outlook.com"
PASSWORD_EMAIL = 'MorEran1302'

def check_valid_password(pas:str) -> bool:
    '''check if the password is valid'''
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)' # contains at least one upper and one lower letter and number.
    return True if re.match(pattern,pas) and len(pas) >= 8 else False # adding the big&equal from 8

def hash_password(plain_password:str) -> str:
    '''encrypt the password user using sha256 algorithm'''
    sha256 = hashlib.sha256()
    sha256.update(plain_password.encode('utf-8'))
    hashed_password = sha256.hexdigest()

    return hashed_password

def email_exists(email:str) -> bool:
    '''exists() method returns True if user_email already in the db'''
    return Users.objects.filter(user_email=email).exists()

def phone_exists(phone:str)-> bool:
    '''returns True if at least one record matches the filter, and False if no records match.'''
    return Users.objects.filter(user_phone=phone).exists()

def full_name_check(full_name:str) -> bool:
    '''
    check if the full name is valid
    full name must be at least 4 characters and contain at least one space.
    '''
    return True if len(full_name) >= 4 and full_name.count(' ') > 0 else False

def phone_number_check(phone_number:str) -> bool:
    '''
    check if the phone number is valid.
    phone number must be at least 10 characters.    
    '''
    return True if len(phone_number) == 10 else False

@api_view(['POST'])
@csrf_exempt
def register(request, user_id = 0): 
    '''
    This function will be used to add a new user.
    user_id = 0, start user_id from 0 and increment by 1 each time a new user is added.
    MORE FROM THE FUNCTION:
    1. check if the email and phone number already exist in the db.
    2. check if the full name, phone number, and password are valid.
    3. encrypt the password before saving it to the db.
    4. save the user to the db.
    '''

    try:
        user_data = request.data 
        
        user_full_name = user_data.get('user_full_name')
        user_email = user_data.get('user_email').lower() # lower case email
        user_phone_number = user_data.get('user_phone')
        user_password = user_data.get('user_password')
        user_password_2 = user_data.get('user_password_2')

        # checks valid register input from user
        check_full_name: bool = full_name_check(user_full_name)
        check_email = validate_email(user_email)
        check_phone_number = phone_number_check(user_phone_number)
        check_password = check_valid_password(user_password)

        if user_password == user_password_2: # checking if 2 user passwords are equal

            user_data['user_password'] = hash_password(user_password) # encrypt before saving

            if email_exists(user_email): 
                return HttpResponseServerError('Email already exists')
            
            if phone_exists(user_phone_number):
                return HttpResponseServerError('Phone number already exists')
            
            if not check_full_name:
                return HttpResponseServerError('Invalid full name')
            
            if not check_phone_number:
                return HttpResponseServerError('Invalid phone number')
            
            if not check_password:
                return HttpResponseServerError('Invalid password')
            
            if not check_email:
                return HttpResponseServerError('Invalid email')

            del user_data['user_password_2'] # don't needs to be save in the db
            
            users_serializer = UsersSerializer(data=user_data)
            if users_serializer.is_valid():
                users_serializer.save() # save to db
                return JsonResponse("Register Success",safe=False)
            else:
                logger.debug(users_serializer.errors)
                return HttpResponseServerError("Register Fails")
        else:
            return HttpResponseServerError("Passwords don't match.")
            
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error parsing user registering data")
    
@api_view(['POST'])
@csrf_exempt
def login(request):
    '''
    This function will be used to login a user.
    1. check if the email exists in the db.
    2. encrypt the password before comparing it to the password in the db.
    3. check if the passwords match.
    '''
    try:
        user_data = request.data

        login_email_address = user_data.get('user_email').lower() # lower case email 
        login_password = user_data.get('user_password')

        # encrypt user password for check similarity in the db
        hash_password_login = hash_password(login_password) 
    
        user = Users.objects.get(user_email=login_email_address) # retrieve user from db based on email

        if user.user_password == hash_password_login:

            response_data = {
            'user': {
                'user_id': user.user_id,
                'user_full_name': user.user_full_name,
                'user_email': user.user_email,
                'user_phone': user.user_phone
            },
                'message': 'Passwords match. Login successfully'
            }
            
            return JsonResponse(response_data)
        else:
            return HttpResponseServerError("Passwords don't match. Login fail")
        
    except Users.DoesNotExist:
        return HttpResponseServerError("User not found.")
    
    except Exception as e:
        logger.error('Error parsing user login data: %s', e)
        return HttpResponseServerError("Error parsing user login data")

@api_view(['GET'])
@csrf_exempt
def tenant_review(request, user_id):
    '''
    This function will returns the tenant reviews that owners will give on the tenant.
    '''
    pass

@api_view(['DELETE'])
@csrf_exempt    
def delete_user(request, user_id):
    '''
    This function will be used to delete a user from the db.
    '''
    try:
        user = Users.objects.get(user_id=user_id)
        user.delete()
        return JsonResponse('Delete successfully', safe=False)
    except Exception as e:
        logger.error('Error deleting user: %s', e)
        return HttpResponseServerError("Error deleting user")

def generate_random_digits() -> str:
    return ''.join(random.choice('0123456789') for _ in range(6))

@api_view(['GET'])
@csrf_exempt
def forget_password(request):
    try:

        user_email = request.data.get('user_email').lower() # lower case email\

        confirm_code = generate_random_digits()
        msg = f'קוד האימות שלך הוא: {confirm_code}'

        # send email to user email with a 6 digit code
        send_email(FROM_EMAIL,user_email,msg)
        #! needs to figure out how to send the confirm_code and the user_email to the front
        return JsonResponse(f"Email sent successfully with code : {confirm_code} with email {user_email}", safe=False)

    except Exception as e:
        logger.error('Error forget password: %s', e)
        return HttpResponseServerError("Error forget password")
    
@api_view(['PUT'])
@csrf_exempt
def reset_password(request):
    try:
        user_email = request.data.get('user_email').lower() # lower case email
        user_code_input = request.data.get('user_code_input')
        user_code_send = request.data.get('user_code_send')
        user_password = request.data.get('user_password')
        user_password_2 = request.data.get('user_password_2')

        if user_code_input != user_code_send:
            return HttpResponseServerError("Code is incorrect")

        if user_password == user_password_2: # checking if 2 user passwords are equal
            user = Users.objects.get(user_email=user_email) # retrieve user from db based on email
            user.user_password = hash_password(user_password) # encrypt before saving
            user.save()
            return JsonResponse("Password reset successfully", safe=False)
        else:
            return HttpResponseServerError("Passwords don't match.")
    except Exception as e:
        logger.error('Error reset password: %s', e)
        return HttpResponseServerError("Error reset password")

    
def send_email(sender_email:str,receiver_email: str, message: str) -> None:
    try:
        # Create the base text message.
        msg = EmailMessage()
        msg["Subject"] = 'איפוס סיסמה'
        msg["From"] = formataddr(("Weather", f"{sender_email}"))
        msg["To"] = receiver_email

        msg.set_content(message)

        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, PASSWORD_EMAIL)
            server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
        logger.error('Error send email: %s', e)
        return HttpResponseServerError("Error send email")
    