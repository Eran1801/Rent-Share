from email.utils import formataddr
import random
import smtplib
from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from django.http import *
from rest_framework.decorators import api_view
from Users.models import Users
from Users.serializers import UsersSerializer
import re
import hashlib
import logging
from email.message import EmailMessage
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PORT = os.environ.get('EMAIL_PORT')
EMAIL_SERVER = os.environ.get('EMAIL_SERVER')
FROM_EMAIL = os.environ.get('COMPANY_EMAIL')
PASSWORD_EMAIL = os.environ.get('EMAIL_PASSWORD')

def generate_random_digits() -> str:
    return ''.join(random.choice('0123456789') for _ in range(4))

def send_email(sender_email,receiver_email,message,subject):

    try:
        # Create the base text message.
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr(("Rent Share", f"{sender_email}"))
        msg["To"] = receiver_email

        msg.set_content(message)

        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, PASSWORD_EMAIL)
            server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
        logger.error('Error send email: %s', e)
        return HttpResponseServerError("Error send email")

def check_valid_password(pas:str) -> bool:

    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)' # contains at least one upper and one lower letter and number.

    return True if re.match(pattern,pas) and len(pas) >= 8 else False

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

    space_place = full_name.find(' ') # to ensure that there is a space in the full name
    return True if len(full_name) >= 3 and space_place != -1 and len(full_name[space_place:]) > 0 else False

def phone_number_check(phone_number:str) -> bool:
    '''
    check if the phone number is valid.
    phone number must be at least 10 characters.    
    '''

    return True if len(phone_number) == 10 and phone_number.isdigit() else False

@api_view(['POST'])
@csrf_exempt
def register(request, user_id = 0): 

    try:
        user_data = request.data 
        
        # extract data
        user_full_name = user_data.get('user_full_name')
        user_email = user_data.get('user_email').lower() # lower case email
        user_phone_number = user_data.get('user_phone')
        user_password = user_data.get('user_password')
        user_password_2 = user_data.get('user_password_2')

        # checks valid register input from user
        check_full_name: bool = full_name_check(user_full_name)
        check_phone_number = phone_number_check(user_phone_number)
        check_password = check_valid_password(user_password)

        if user_password == user_password_2: # checking if 2 user passwords are equal

            # return associated error message if the input is invalid
            if check_full_name is False:
                return HttpResponseServerError('Invalid full name')

            if email_exists(user_email) is True: 
                return HttpResponseServerError('Email already exists')
            
            if phone_exists(user_phone_number) is True:
                return HttpResponseServerError('Phone number already exists')
            
            if check_phone_number is False:
                return HttpResponseServerError('Invalid phone number')
            
            if check_password is False:
                return HttpResponseServerError('Invalid password')

            del user_data['user_password_2'] # don't needs to be save in the db after checking
            user_data['user_password'] = hash_password(user_password) # encrypt before saving

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
        return HttpResponseServerError("Error in register function")
    

@api_view(['POST'])
@csrf_exempt
def login(request):

    try:
        user_data = request.data

        # extract the right data
        login_email_address = user_data.get('user_email').lower() # lower case email 
        login_password = user_data.get('user_password')

        # encrypt user password for check similarity in the db
        hash_password_login = hash_password(login_password) 

        # retrieve user from db based on email
        user = Users.objects.get(user_email=login_email_address)

        if user.user_password == hash_password_login:
            
            # sending to the frontend
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
            return HttpResponseServerError("Passwords Incorrect. Login fail")
        
    except Users.DoesNotExist:
        return HttpResponseServerError("Email don't exists. Login fail")
    
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error in login function")


@api_view(['DELETE'])
@csrf_exempt    
def delete_user(request):

    try:
        # get operation diff in extract data
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id) # from db

        # delete user, posts, messages from db
        user.delete() 

        return JsonResponse('Delete successfully', safe=False)
    
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error deleting user function")


@api_view(['GET'])
@csrf_exempt
def forget_password(request):
    try:
        
        # extract the user email
        user_email = request.GET.get('user_email').lower() # lower case email

        # first check if the email is in the db, if the user doesn't exist, return error
        if email_exists(user_email) is False:
            return HttpResponseServerError('Email dont exists')

        confirm_code = generate_random_digits()
        msg = f'קוד האימות שלך הוא : {confirm_code}\nהקוד תקף ל-5 דקות'
        subject = 'איפוס סיסמה'

        # send email to user email with a 6 digit code
        send_email(FROM_EMAIL,user_email,msg,subject)
        
        response_data = {
            'user': {
                'user_email': user_email,
                'confirm_code': confirm_code,
            },
                'message': f"Email sent successfully with code : {confirm_code} with email {user_email}"
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        logger.error('Error forget password: %s', e)
        return HttpResponseServerError("Error forget password function")
    

@api_view(['PUT'])
@csrf_exempt
def reset_password(request):
    try:

        data = request.data

        # extract the right data
        user_email = data.get('user_email').lower() # lower case email
        user_password = data.get('user_password')
        user_password_2 = data.get('user_password_2')

        if check_valid_password(user_password) is False:
            return HttpResponseServerError("Password is invalid")

        if user_password == user_password_2: # checking if 2 user passwords are equal

            # retrieve user from db based on email
            user = Users.objects.get(user_email=user_email)

            # encrypt before saving
            user.user_password = hash_password(user_password) 

            user.save()

            return JsonResponse("Password reset successfully", safe=False)
        else:
            return HttpResponseServerError("Passwords don't match.")
        
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error reset password function")