from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from Users.UserAuth.decorators import jwt_required
from Users.models import Users
from django.db import transaction
from Users.serializers import UserSerializerPicture, UserSerializerProfileDetails
from Users.utilities import encrypt_password, error_response, success_response, validate_change_password_data, validate_update_user_info

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
        return error_response("User not found")

    except Exception as e:
        return error_response(f"An error occurred during personal info update,  {e}")


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
        with transaction.atomic():
            user.save()

        return success_response(message="Password updated successfully")

    except Users.DoesNotExist:
        return error_response("User not found")

    except Exception as e:
        return error_response(f"An error occurred during password update {e}")


@api_view(['PUT'])
@csrf_exempt
@jwt_required
@parser_classes([MultiPartParser, FormParser])
def change_profile_picture(request):
    """
    This function will be used to change the user's personal_info picture.
    The function gets profile image in form-data.
    """
    try:
        user = Users.objects.get(user_id=request.user_id)
        user_serializer = UserSerializerPicture(instance=user, data=request.data, partial=True)

        if user_serializer.is_valid():
            with transaction.atomic():
                user_serializer.save()
                return success_response(message="Profile picture successfully saved in db")
       
        return error_response(f"An error occurred during personal_info picture upload, {user_serializer.errors}")

    except Users.DoesNotExist:
        return error_response("User not found")
    
    except Exception as e:
        return error_response(f"An error occurred during personal_info picture upload, {e}")

@api_view(['GET'])
@csrf_exempt
@jwt_required
def get_user_details(request):
    try:

        user = Users.objects.get(user_id=request.user_id)

        user_serializer = UserSerializerProfileDetails(instance=user, many=False, partial=True)
        return success_response(user_serializer.data)

    except Users.DoesNotExist:
        return error_response("User not found")

    except Exception as e:
        return error_response(f"An error occurred during personal_info picture upload {e}")