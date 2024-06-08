from venv import logger
from django.db import transaction
from Users.auth.decorators import jwt_required
from Users.utilities import encrypt_password, error_response, set_cookie_in_response, success_response, validate_register_data
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from Users.models import Users
from Users.serializers import UsersSerializer
from Users.auth.backends import CustomBackend
from rest_framework.parsers import JSONParser



@api_view(['POST'])
@csrf_exempt
def register(request):
    try:
        
        request.data['user_email'] = request.data.get('user_email', '').lower() # set user mail to lower before saving

        # validation checks for user details
        error_message = validate_register_data(request.data)
        if error_message:
            return error_response(message=error_message)

        del request.data['user_password_2']  # no longer needed after validation
        request.data['user_password'] = encrypt_password(request.data.get('user_password'))

        users_serializer = UsersSerializer(data=request.data)
        if users_serializer.is_valid():
            with transaction.atomic():
                users_serializer.save()
            
            return success_response(message="User created successfully")
        else:
            return error_response(message=users_serializer.errors)

    except Exception as e:
        return error_response(message=f"Error in register function, {e}")


@api_view(['POST'])
@csrf_exempt
def login(request):
    try:
        # Extract the right data
        email = request.data.get('user_email')
        password = request.data.get('user_password')

        email = email.lower()  # lower case email

        # Authenticate user
        user = CustomBackend().authenticate(request, username=email, password=password)
        
        if user:
            # response = set_cookie_in_response(user, request)
            # return response
            logger.info(f'user email - {user.user_email}\nuser password - {user.user_id}')
            return success_response(user.user_email)

        return error_response("email or password incorrect")

    except Exception as e:
        logger.error(f"Error in login function: {e}")
        return error_response(message=f"Error in login function, {e}")

@api_view(['DELETE'])
@csrf_exempt
@jwt_required
def delete_user(request):
    try:
        user = Users.objects.get(user_id=request.user_id)

        # delete user, posts, messages from db
        user.delete()

        return success_response(message="Delete successfully")

    except Users.DoesNotExist:
        return error_response("User not found")

    except Exception as e:
        return error_response(message=f"Error deleting user function, {e}")