import logging
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from Posts.utilities import convert_base64
from Users.auth.decorators import jwt_required
from Users.models import Users
from django.db import transaction
from Users.serializers import UserSerializerPicture
from Users.utilities import encrypt_password, error_response,check_valid_password, success_response, validate_change_password_data, validate_update_user_info

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@api_view(['PUT'])
@csrf_exempt
@jwt_required
def change_personal_info(request):
    '''This function will be used to change the user's personal info'''

    try:
        user = Users.objects.get(user_id=request.user_id)

        full_name = request.data.get('user_full_name')
        phone = request.data.get('user_phone')
        email = request.data.get('user_email')

        response = validate_update_user_info(user, full_name, email, phone)

        if response != 'success':
            return error_response(message=response)
        
        with transaction.atomic():
            user.save()
            
        return success_response(message="Personal info updated successfully")

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        return HttpResponseServerError(f"An error occurred during personal info update,  {e}")


@api_view(['PUT'])
@csrf_exempt
@jwt_required
def change_password(request):
    '''This function will be used to change the user's password'''

    try:
        user = Users.objects.get(user_id=request.user_id)
        
        response = validate_change_password_data(request, user)
        if response: # if the validate function returns error, return it
            return response

        user.user_password = encrypt_password(request.data.get('new_password'))
        user.save()

        return success_response(message="Password updated successfully")

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        return HttpResponseServerError(f"An error occurred during password update {e}")


@api_view(['PUT'])
@csrf_exempt
@jwt_required
def change_profile_picture(request):
    '''
        This function will be used to change the user's personal_info picture
        The function gets profile image in base64
    '''

    try:

        profile_image_base64 = request.data.get('profile_image')
        profile_image_file = convert_base64(profile_image_base64, "profile_image")

        data = {'user_profile_pic': profile_image_file}

        user = Users.objects.get(user_id=request.user_id)
        user_serializer = UserSerializerPicture(instance=user, data=data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()
            return success_response(message="Profile picture successfully saved in db")
       
        return error_response(f"An error occurred during personal_info picture upload, {user_serializer.errors}")

    except Exception as e:
        return error_response(f"An error occurred during personal_info picture upload, {e}")


@api_view(['GET'])
@csrf_exempt
@jwt_required
def get_profile_pic(request):
    try:
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id)

        user_serializer = UserSerializerPicture(instance=user, many=False, partial=True)
        return success_response(user_serializer.data)

    except Users.DoesNotExist:
        return error_response("User not found")

    except Exception as e:
        return error_response(f"An error occurred during personal_info picture upload {e}")