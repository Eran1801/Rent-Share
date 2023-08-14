from django.db import connection
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser

from Users.models import Users
from Users.serializers import UsersSerializer
import re
import hashlib
import logging
from validate_email import validate_email

# Define the logger at the module level
logger = logging.getLogger(__name__)

def check_valid_password(pas:str) -> bool:
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)' # contains at least one upper and one lower letter and number.
    return True if re.match(pattern,pas) and len(pas) >= 8 else False # adding the big&equal from 8

def hash_password(plain_password:str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(plain_password.encode('utf-8'))
    hashed_password = sha256.hexdigest()

    return hashed_password

def email_exists(email:str) -> bool:
    '''exists() method returns True if user_email already in the db'''
    return Users.objects.filter(user_email=email).exists()

def phone_exists(phone:str)-> bool:
    return Users.objects.filter(user_phone=phone).exists()


#! HOW TO REMOVE ALL THE REGISTERS USERS IN THE DATA BASE ?!! 

@csrf_exempt
def register(request, user_id = 0): 

    logging.basicConfig(level=logging.DEBUG)

    if request.method == 'POST':
        user_data = JSONParser().parse(request) # access individual fields, users_data.get('field_name')
        
        user_full_name = user_data.get('user_full_name')
        user_email = user_data.get('user_email').lower() # lower case email
        user_phone_number = user_data.get('user_phone')
        user_password = user_data.get('user_password')
        user_password_2 = user_data.get('user_password_2')
        
        # checks valid register input from user
        check_full_name: bool = True if len(user_full_name) >= 4 and user_full_name.count(' ') > 0 else False
        check_email = validate_email(user_email)
        check_phone_number = True if len(user_phone_number) >= 10 else False
        check_password = check_valid_password(user_password)

        if user_password == user_password_2: # checking if 2 user passwords are equal
            if email_exists(user_email):
                return JsonResponse('Email already exists',safe=False)
            if phone_exists(user_phone_number):
                return JsonResponse('Phone number already exists',safe=False)
            
            user_data['user_password'] = hash_password(user_password) # encrypt before saving
            if check_full_name and check_phone_number and check_password and check_email: # check if all true
                    del user_data['user_password_2']
                    users_serializer = UsersSerializer(data=user_data)
                    if users_serializer.is_valid():
                        users_serializer.save() # save to db
                        return JsonResponse("Register Success", safe=False)
                    else:
                        logger.debug(users_serializer.errors)
                        return JsonResponse("Register Fails", safe=False)
            else:
                return JsonResponse('Something wrong with name|phone|password|email',safe=False)
        else:
            return JsonResponse("Passwords don't match.", safe=False)
        
    elif request.method == 'GET':
        users = Users.objects.all()
        users_serializer = UsersSerializer(users, many=True)
        return JsonResponse(users_serializer.data, safe=False)
        
@csrf_exempt
def login(request):
    if request.method == 'GET':
        
        user_data = JSONParser().parse(request)

        login_email_address = user_data.get('user_email').lower() # lower case email 
        login_password = user_data.get('user_password')

        # encrypt user password for check similarity in the db
        hash_password_login = hash_password(login_password) 
        
        try:
            user = Users.objects.get(user_email=login_email_address) # retrieve user from db based on email
            if user.user_password == hash_password_login:
                return JsonResponse("Passwords match. Login successfully", safe=False)
            else:
                return JsonResponse("Passwords don't match. Login fail", safe=False)
        except Users.DoesNotExist:
            return JsonResponse("User not found.", safe=False)
        
      