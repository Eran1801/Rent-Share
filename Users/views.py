# from django.http.response import JsonResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import \
#     csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
# from rest_framework.parsers import JSONParser

# from Users.models import Users
# from Users.serializers import UsersSerializer

# '''
# By adding @csrf_exempt to the view function, you're telling Django that
# this view doesn't require CSRF protection.
# This allows your Angular frontend to make POST, PUT, and DELETE requests
# to the API without including CSRF tokens in those requests.
# '''
# @csrf_exempt
# def users_api(request, user_id=0):
#     if request.method == 'GET':
#         users = Users.objects.all()
#         users_serializer = UsersSerializer(users, many=True)
#         return JsonResponse(users_serializer.data, safe=False)
#     elif request.method == 'POST':
#         users_data = JSONParser().parse(request)
#         users_serializer = UsersSerializer(data=users_data)
#         if users_serializer.is_valid():
#             users_serializer.save()
#             return JsonResponse("Added Successfully!!", safe=False)
#         return JsonResponse("Failed to Add.", safe=False)
    # elif request.method == 'PUT':
    #     users_data = JSONParser().parse(request)
    #     users = Users.objects.get(user_id=users_data['user_id'])
    #     users_serializer = UsersSerializer(users, data=users_data)
    #     if users_serializer.is_valid():
    #         users_serializer.save()
    #         return JsonResponse("Updated Successfully!!", safe=False)
    #     return JsonResponse("Failed to Update.", safe=False)
#     elif request.method == 'DELETsE':
#         users = Users.objects.get(user_id=user_id)
#         users.delete()
#         return JsonResponse("Deleted Successfully!!", safe=False)

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
# from validate_email import validate_email


def check_password(pas:str) -> bool:
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)' # contains at least one upper in the begging and lower letter and number
    return True if re.match(pattern,pas) and len(pas) >= 8 else False # adding the big&equal from 8

# def check_email(email:str) -> [bool,str]:
#     try:
#         email_info = validate_email(email,validate_email=True)
#         return [True,email]
#     except:
#         return [False, 'Email not valid']

def hash_password(plain_password:str):
    sha256 = hashlib.sha256()
    sha256.update(plain_password.encode('utf-8'))
    hashed_password = sha256.hexdigest()

    return hashed_password

@csrf_exempt
def register(request, user_id = 0): 

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)  # Get logger instance

    if request.method == 'POST':
        user_data = JSONParser().parse(request) # access individual fields, users_data.get('field_name')
        
        password_s:str = user_data.get('user_password')

        # checks valid register input from user
        full_name = True if len(user_data.get('user_full_name')) > 4 else False
        # email = check_email(user_data.get('user_email'))
        phone_number = True if len(user_data.get('user_phone')) >= 10 else False #! MAYBE USE TEMPLATE OF COUNTRY AND PHONE NUMBER
        password_b:bool = check_password(user_data.get('user_password'))
        password_2 = user_data.get('user_password_2') #! tell mor send from front also

        logger.debug(f'Debug message: full_name = {full_name}\nphone_number = {phone_number}\npassword = {password_s}\npassword2 = {password_2}\nemail = {user_data.get("user_email")}')

        if password_s == password_2: # checking if 2 user passwords is equal
            user_data['user_password'] = hash_password(user_data['user_password']) # encrypt before saving
            if full_name and phone_number and password_b: # check if all true, remove the email[0]
                    users_serializer = UsersSerializer(data=user_data)
                    if users_serializer.is_valid():
                        users_serializer.save() # to db
                        return JsonResponse("Register Success", safe=False)
                    else:
                        logger.debug(users_serializer.errors)
                        return JsonResponse("Register Fails", safe=False)
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

        login_email_address = user_data.get('login_email')
        login_password = user_data.get('login_password')

        # encrypt user password for check similarity in the db
        hash_password_login = hash_password(login_password) 

        # with connection.cursor() as cursor:
        #     query = "SELECT user_password FROM Users_users WHERE user_email = %s and password = %s"
        #     cursor.execute(query, (login_email_address,hash_password_login))
        #     user_record = cursor.fetchone()
        #     if hash_password_login == user_record[1]: # hash password from db
        #         redirect('/home') 
            
        
        # more secure option / needs to exam:
        try:
            user = Users.objects.get(user_email=login_email_address) # retrieve user from db based on email
            if user.user_password == hash_password_login:
                return JsonResponse("Passwords match.", safe=False)
            else:
                return JsonResponse("Passwords don't match.", safe=False)
        except Users.DoesNotExist:
            return JsonResponse("User not found.", safe=False)
        
        # TODO : add a function that gets the email of the user and checks if it's unique.
        # TODO : checks if it's already in the db 