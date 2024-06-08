from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from django.http import *
from rest_framework.decorators import api_view
from django.db import transaction
from Users.models import PasswordResetCode, Users
from Users.utilities import check_valid_password, check_verification_code_expiry, email_exists, encrypt_password, error_response, generate_verification_code, send_email, success_response
from Inbox.msg_emails_Enum import FROM_EMAIL, Emails


@api_view(['POST'])
@csrf_exempt
def forget_password(request):
    """This function will be used to send a 4 digit code to the user email to reset the password."""
    try:
        user_email = request.get('user_email').lower()  # lower case email

        if email_exists(user_email) is False:
            return error_response(message="Email doesn't exist")

        verification_code = generate_verification_code()
        msg = Emails.FORGET_PASSWORD_MESSAGE.value % verification_code  
        subject = Emails.FORGET_PASSWORD_SUBJECT

        send_email(FROM_EMAIL, user_email, msg, subject)

        password_verification_code = PasswordResetCode.objects.create(verification_code=verification_code)
        with transaction.atomic():
            password_verification_code.save()

        return success_response(data=password_verification_code.id, message="Email sent successfully")

    except Exception as e:
        return error_response(message=f"Error in forget password function {e}")


@api_view(['POST'])
@csrf_exempt
def verify_code(request):
    """This function will be used to verify the code that the user received by email"""
    try:
        verification_code = request.data.get('verification_code')
        verification_code_id = request.data.get('verification_code_id')
        
        password_reset_code = PasswordResetCode.objects.get(id=verification_code_id)

        if check_verification_code_expiry(verification_code,password_reset_code) is False:
            if password_reset_code.verification_code == verification_code:
                return success_response(message="Code verified successfully")
            else:
                return error_response(message="Code is incorrect")
        else:
            return error_response(message="Code expired")
    
    except Exception as e:
        return error_response(message=f"Error in verify code function {e}")


@api_view(['PUT'])
@csrf_exempt
def reset_password(request):
    """This function will be reset the user password inside the forget-password flow"""
    try:
                
        user_email = request.data.get('email').lower() # needs to be saved in session from step 1 on client
        
        user = Users.objects.get(user_email=user_email)
        if not user:
            return error_response("User with this email not found")

        password = request.data.get('password')
        password2 = request.data.get('confirm_password')

        if check_valid_password(password) is False:
            return error_response(message="Password is invalid")

        if password == password2:  # checking if 2 passwords are equal
            user.user_password = encrypt_password(password) # update in the db
            with transaction.atomic():
                user.save()

            return success_response(message="Password reset successfully")
        
        return error_response(message="Passwords don't match")
        
    except Users.DoesNotExist:
        return error_response("User not found")

    except Exception as e:
        return error_response(message=f"Error in reset password function, {e}")