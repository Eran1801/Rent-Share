from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from django.http import *
from rest_framework.decorators import api_view

from Users.models import PasswordResetCode
from Users.utilities import *
from Users.utilities import FROM_EMAIL
from Inbox.msg_emails_Enum import Emails
from django.core.exceptions import ObjectDoesNotExist


EMAIL_SUBJECT = 'איפוס סיסמה'


@api_view(['GET'])
@csrf_exempt
def forget_password(request):
    """This function will be used to send a 6 digit code to the user email to reset the password."""
    try:
        user_email = request.GET.get('user_email').lower()  # lower case email

        if email_exists(user_email) is False:
            return error_response(message="Email doesn't exist")

        verification_code = generate_verification_code()
        msg = Emails.FORGET_PASSWORD_MESSAGE.value % verification_code  
        subject = EMAIL_SUBJECT

        send_email(FROM_EMAIL, user_email, msg, subject)

        password_verification_code = PasswordResetCode.objects.create(verification_code=verification_code)
        password_verification_code.save()
        
        response = {
            'verification_code_id': password_verification_code.id,
            'message': 'Email sent successfully'
        }

        return success_response(data=response, message="Email sent successfully")

    except Exception as e:
        logger.error('Error forget password: %s', e)
        return error_response(message="Error in forget password function")

@api_view(['POST'])
@csrf_exempt
def verify_code(request):
    """This function will be used to verify the code that the user received by email"""
    try:
        data = request.data
        verification_code = data.get('verification_code')
        verification_code_id = data.get('verification_code_id')
        
        password_reset_code = PasswordResetCode.objects.get(id=verification_code_id)

        if check_verification_code_expiry(verification_code,password_reset_code) is False:
            if password_reset_code.verification_code == verification_code:
                return success_response(message="Code verified successfully")
            else:
                return error_response(message="Code is incorrect")
        else:
            return error_response(message="Code expired")
        
    except ObjectDoesNotExist:
        return error_response(message="Verification code not found", status=404)
    
    except Exception as e:
        logger.error('Error verify code: %s', e)
        return error_response(message="Error in verify code function")

@api_view(['PUT'])
@csrf_exempt
def reset_password(request):
    """This function will be reset the user password inside the forget-password flow"""
    try:
        data = request.data

        user_email = data.get('user_email').lower()
        user = Users.objects.get(user_email=user_email)

        password = data.get('user_password')
        password2 = data.get('user_password_2')

        if check_valid_password(password) is False:
            return error_response(message="Password is invalid")

        if password == password2:  # checking if 2 passwords are equal
            user.user_password = encrypt_password(password)
            user.save()

            return success_response(message="Password reset successfully")
        else:
            return error_response(message="Passwords don't match.")

    except Exception as e:
        logger.error(e)
        return error_response(message="Error in reset password function")