from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
import Users
from Users.views import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['PUT'])
@csrf_exempt
def change_personal_info(request):
    '''This function will be used to change the user's personal info'''

    try:
        user_data = request.data

        user_id = user_data.get('user_id')
        logger.info(f'User ID: {user_id}')

        full_name = user_data.get('user_full_name')
        logger.info(f'Full name: {full_name}')

        phone = user_data.get('user_phone')
        logger.info(f'Phone: {phone}')

        email = user_data.get('user_email')
        logger.info(f'Email: {email}')
        
        user = Users.objects.get(user_id=user_id)  # Get the user from the database by user_id

        # Check if fields have changed
        if full_name != user.user_full_name:
            if full_name_check(full_name) == False:
                return HttpResponseServerError("Full name is invalid")
            else:
                user.user_full_name = full_name

        logger.info('Passed full name check')

        if email != user.user_email:
            if validate_email(email) == False:
                return HttpResponseServerError("Email is invalid")
            if email_exists(email) == True:
                return HttpResponseServerError("Email already exists in our system")
            user.user_email = email

        logger.info('Passed email check')

        if phone != user.user_phone:
            if phone_number_check(phone) == False:
                return HttpResponseServerError("Phone number is invalid")
            if phone_exists(phone) == True:
                return HttpResponseServerError("Phone number already exists in our system")
            user.user_phone = phone
        
        logger.info('Passed phone check')

        user.save()  # save changes to the database
        return JsonResponse("Personal info updated successfully", safe=False)

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred")
    
@api_view(['PUT'])
@csrf_exempt
def change_password(request):
    '''This function will be used to change the user's password'''

    try:
        user_data = request.data

        old_password = hash_password(user_data.get('old_password')) # encrypt the old password
        new_password = user_data.get('new_password')
        new_password_confirm = user_data.get('new_password_confirm')

        user = Users.objects.get(user_id=user_data.get('user_id')) # get the user from the database by user_id
        
        # check if the old password is correct
        if user.user_password != old_password:
            return HttpResponseServerError("Old password is incorrect")
        
        if new_password != new_password_confirm:
            return HttpResponseServerError("Passwords don't match")
        
        if check_valid_password(new_password) == False:
            return HttpResponseServerError("Password is invalid")
        
        user.user_password = hash_password(new_password) # update the password
        user.save() # save changes to the database

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")
    
    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred")
    
# @api_view(['PUT'])
# @csrf_exempt
# def change_profile_picture(request):
#     '''This function will be used to change the user's profile picture'''

#     try:
#         user_data = request.data

#         user = Users.objects.get(user_id=user_data['user_id']) # get the user from the database by user_id

#         user.user_profile_picture = user_data.get('user_profile_picture') # update the profile picture
#         user.save() # save changes to the database

#     except Users.DoesNotExist:
#         return HttpResponseServerError("User not found")
    
#     except Exception as e:
#         logger.error(f'Error: {e}')
#         return HttpResponseServerError("An error occurred")
    

