from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
import Users
from Users.views import hash_password

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@api_view(['PUT'])
@csrf_exempt
def change_personal_info(request):

@api_view(['PUT'])
@csrf_exempt
def change_personal_info(request):
    '''This function will be used to change the user's personal info'''

    try:
        user_data = request.data  # Use request.data to parse JSON
        user_id = user_data['user_id']
        
        user = Users.objects.get(user_id=user_id)  # Get the user from the database by user_id

        # Check if fields have changed
        if user_data['user_full_name'] != user.user_full_name:
            if Users.full_name_check(user_data['user_full_name']) == False:
                return HttpResponseServerError("Full name is invalid")
            else:
                user.user_full_name = user_data['user_full_name']

        if user_data['user_email'] != user.user_email:
            if Users.validate_email(user_data['user_email']) == False:
                return HttpResponseServerError("Email is invalid")
            if Users.email_exists(user_data['user_email']) == False:
                return HttpResponseServerError("Email already exists in our system")
            user.user_email = user_data['user_email']

        if user_data['user_phone'] != user.user_phone:
            if Users.phone_number_check(user_data['user_phone']) == False:
                return HttpResponseServerError("Phone number is invalid")
            if Users.phone_exists(user_data['user_phone']) == False:
                return HttpResponseServerError("Phone number already exists in our system")
            user.user_phone = user_data['user_phone']

        user.save()  # Save changes to the database
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

        old_password = hash_password(user_data['old_password'])
        new_password = user_data['new_password']
        new_password_confirm = user_data['new_password_confirm']

        user = Users.objects.get(user_id=user_data['user_id']) # get the user from the database by user_id
        
        # check if the old password is correct
        if user.user_password != old_password:
            return HttpResponseServerError("Old password is incorrect")
        
        if new_password != new_password_confirm:
            return HttpResponseServerError("Passwords don't match")
        
        if not Users.validate_password(new_password):
            return HttpResponseServerError("Password is invalid")
        
        user.user_password = hash_password(new_password) # update the password
        user.save() # save changes to the database

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")
    
    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred")
    
@api_view(['PUT'])
@csrf_exempt
def change_profile_picture(request):
    '''This function will be used to change the user's profile picture'''

    try:
        user_data = request.data

        user = Users.objects.get(user_id=user_data['user_id']) # get the user from the database by user_id

        user.user_profile_picture = user_data['user_profile_picture'] # update the profile picture
        user.save() # save changes to the database

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")
    
    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred")