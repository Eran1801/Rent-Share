import logging

from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from Posts.utilities import convert_base64
from Users.auth.utils_auth import encrypt_password
from Users.models import Users
from Users.personal_info.personal_info_util import validate_update_user_info
from Users.serializers import UserSerializerPicture
from Users.utilities import email_exists, check_email_valid, phone_exists, phone_number_check, full_name_check, \
    check_valid_password


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['PUT'])
@csrf_exempt
def change_personal_info(request):
    '''This function will be used to change the user's personal info'''

    try:
        user_data = request.data

        # extract nesscrery data
        user_id = user_data.get('user_id')
        full_name = user_data.get('user_full_name')
        phone = user_data.get('user_phone')
        email = user_data.get('user_email')

        user = Users.objects.get(user_id=user_id)  # get the user from the database by user_id

        response = validate_update_user_info(user, full_name, email, phone)

        if response != "success":
            return JsonResponse(response,safe=False, status=400)
        
        user.save()  # save changes to the database
        return JsonResponse("Personal info updated successfully", safe=False)

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during personal info update")


@api_view(['PUT'])
@csrf_exempt
def change_password(request):
    '''This function will be used to change the user's password'''

    try:
        user_data = request.data

        new_password = user_data.get('new_password')
        new_password_confirm = user_data.get('new_password_confirm')

        user = Users.objects.get(user_id=user_data.get('user_id'))  # get the User from the database by user_id

        # check if the old password is correct
        if user.check_password(user_data.get('old_password')) is False:
            return JsonResponse("Old password is incorrect",safe=False, status=400)

        if new_password != new_password_confirm:
            return JsonResponse("Passwords don't match.", safe=False, status=400)

        if check_valid_password(new_password) is False:
            return JsonResponse("Password is invalid",safe=False, status=400)

        # update the password but encrypt is first
        user.user_password = encrypt_password(new_password)

        # save changes to the database
        user.save()

        return JsonResponse("Password updated successfully", safe=False)

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during password update")


@api_view(['PUT'])
@csrf_exempt
def change_profile_picture(request):
    '''This function will be used to change the user's personal_info picture'''

    try:
        user_data = request.data
        user_id = user_data.get('user_id')

        profile_image_base64 = user_data.get('profile_image')
        profile_image_file = convert_base64(profile_image_base64, "profile_image")

        user = Users.objects.get(user_id=user_id)  # get the user from the database by user_id

        data = {'user_profile_pic': profile_image_file}

        # serialize only the photo field that separates the image from the rest of the data
        user_serializer = UserSerializerPicture(instance=user, data=data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()  # attempt to save to the database
            logger.info("Saved to the database")
            return JsonResponse("Profile picture successfully saved in db", safe=False)

        else:
            logger.debug(user_serializer.errors)
            return HttpResponseServerError("An error occurred during personal_info picture upload")

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during personal_info picture upload")


@api_view(['GET'])
@csrf_exempt
def get_profile_pic(request):
    try:
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id)  # get the user from the database by user_id

        user_serializer = UserSerializerPicture(instance=user, many=False, partial=True)
        return JsonResponse(user_serializer.data, safe=False)

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during personal_info picture upload")
