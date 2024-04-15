from Users.utilities import encrypt_password, error_response, success_response, validate_register_data
import logging
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from Users.models import Users
from Users.serializers import UsersSerializer
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['POST'])
@csrf_exempt
def register(request):
    try:
        user_data = request.data
        user_data['user_email'] = user_data.get('user_email', '').lower()

        # Sequential validation checks
        error_message = validate_register_data(user_data)
        if error_message:
            logger.info(f'Error message: {error_message}')
            return error_response(message=error_message)

        del user_data['user_password_2']  # No longer needed after validation
        user_data['user_password'] = encrypt_password(user_data.get('user_password'))

        users_serializer = UsersSerializer(data=user_data)
        if users_serializer.is_valid():
            users_serializer.save()
            return success_response(message="Register Success")
        else:
            return error_response(message=users_serializer.errors)

    except Exception as e:
        logger.error(e)
        return error_response(message="Error in register function")

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
            return success_response(data=response_data, message="Passwords match. Login successfully")

        else:
            return error_response(message="Passwords Incorrect. Login fail")

    except Users.DoesNotExist:
        return error_response(message="Email doesn't exist. Login fail")

    except Exception as e:
        logger.error(e)
        return error_response(message="Error in login function")

@api_view(['DELETE'])
@csrf_exempt
def delete_user(request):
    try:
        # get operation diff in extract data
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id)  # from db

        # delete user, posts, messages from db
        user.delete()

        return success_response(message="Delete successfully")

    except Exception as e:
        logger.error(e)
        return error_response(message="Error deleting user function")