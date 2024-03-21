import logging

from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from Users.models import Users
from Users.serializers import UsersSerializer
from Users.auth.utils_auth import *
from django.contrib.auth import authenticate


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['POST'])
@csrf_exempt
def register(request, user_id=0):
    try:
        user_data = request.data
        user_data['user_email'] = user_data.get('user_email', '').lower()

        # Sequential validation checks
        error_message = validate_register_data(user_data)
        if error_message:
            logger.info(f'Error message: {error_message}')
            return JsonResponse(error_message, status=400, safe=False)

        del user_data['user_password_2']  # No longer needed after validation
        user_data['user_password'] = encrypt_password(user_data.get('user_password'))

        users_serializer = UsersSerializer(data=user_data)
        if users_serializer.is_valid():
            users_serializer.save()
            return JsonResponse("Register Success", status=200, safe=False)
        else:
            return JsonResponse(users_serializer.errors, status=400, safe=False)

    except Exception as e:
        logger.error(e)
        return JsonResponse("Error in register function", safe=False, status=400)


@api_view(['POST'])
@csrf_exempt
def login(request):
    try:
        user_data = request.data

        # extract the right data
        email = user_data.get('user_email').lower()  # lower case email
        password = user_data.get('user_password')

        # Authenticate user
        user = authenticate(username=email, password=password)

        if user:
            response_data = {
                'user': {
                    'user_id': user.user_id,
                    'user_full_name': user.user_full_name,
                    'user_email': user.user_email,
                    'user_phone': user.user_phone
                },
                'message': 'Passwords match. Login successfully'
            }

            return JsonResponse(response_data, safe=False, status=200)
        else:
            return JsonResponse("Passwords Incorrect. Login fail", safe=False, status=400)

    except Users.DoesNotExist:
        return JsonResponse("Email don't exists. Login fail", status=400, safe=False)

    except Exception as e:
        logger.error(e)
        return JsonResponse("Error in login function", safe=False, status=400)


@api_view(['DELETE'])
@csrf_exempt
def delete_user(request):
    try:
        # get operation diff in extract data
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id)  # from db

        # delete user, posts, messages from db
        user.delete()

        return JsonResponse('Delete successfully', safe=False)

    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error deleting user function")
