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
    '''This function will be used to change the user's personal info'''

    try:
        user_data = request.data  # Use request.data to parse JSON

        full_name = user_data['user_full_name']
        email = user_data['user_email']
        phone = user_data['user_phone']

        # check data is valid
        if not Users.full_name_check(full_name):
            return HttpResponseServerError("Full name is invalid")
        elif not Users.validate_email(email):
            return HttpResponseServerError("Email is invalid")
        elif not Users.phone_number_check(phone):
            return HttpResponseServerError("Phone number is invalid")
        elif not Users.phone_exists(phone):
            return HttpResponseServerError("Phone number already exists")
        elif not Users.email_exists(email):
            return HttpResponseServerError("Email already exists")
        
        user = Users.objects.get(user_id=user_data['user_id']) # get the user from the database by user_id

        # update the user info
        user.user_full_name = user_data['user_full_name']
        user.user_email = user_data['user_email']
        user.user_phone = user_data['user_phone']

        user.save()  # save changes to the database

        return JsonResponse("Personal info updated successfully",safe=False)

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