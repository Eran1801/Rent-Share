from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from django.http import *
from rest_framework.decorators import api_view

from Users.auth.auth_util import hash_password
from Users.models import PasswordResetCode
from Users.utilities import *
import logging
from Users.utilities import FROM_EMAIL
from django.utils.safestring import mark_safe

EMAIL_SUBJECT = 'איפוס סיסמה'


@api_view(['GET'])
@csrf_exempt
def forget_password(request):
    """This function will be used to send a 6 digit code to the user email to reset the password."""
    try:

        # extract the user email
        user_email = request.GET.get('user_email').lower()  # lower case email

        # first check if the email is in the db, if the user doesn't exist, return error
        if email_exists(user_email) is False:
            return JsonResponse('Email dont exists', safe=False, status=400)

        verification_code = generate_verification_code()

        # Use dir="rtl" to ensure correct display of RTL text
        msg = mark_safe(f"""
        <html>
            <body>
                <p dir="rtl">שלום רב, אימייל זה נשלח מכיוון שרצית לאפס את הסיסמה שלך</p>
                <p dir="rtl">קוד האימות שלך הוא: <b>{verification_code}</b><br>
                   הקוד תקף ל-5 דקות.
                </p>
            </body>
        </html>
        """)
        subject = EMAIL_SUBJECT

        # send email to user email with a 6-digit code
        send_email(FROM_EMAIL, user_email, msg, subject)

        # Save the confirm_code in the db
        password_reset_code = PasswordResetCode.objects.create(verification_code=verification_code)

        response = {
            'verification_code_id': password_reset_code.id,
            'message': 'Email sent successfully'
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        logger.error('Error forget password: %s', e)
        return JsonResponse("Error forget password function", safe=False, status=400)


@api_view(['POST'])
@csrf_exempt
def verify_code(request):
    """This function will be used to verify the code that the user received by email"""
    try:
        data = request.data
        verification_code = data.get('verification_code')
        verification_code_id = data.get('verification_code_id')

        # check if the code exists in the db
        if PasswordResetCode.objects.filter(id=verification_code_id, verification_code=verification_code).exists():
            return JsonResponse("Code verified successfully", safe=False, status=200)

        return JsonResponse("Code is invalid", safe=False, status=400)

    except Exception as e:
        logger.error('Error verify code: %s', e)
        return JsonResponse("Error verify code function", safe=False, status=400)


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
            return JsonResponse("Password is invalid", safe=False, status=400)

        if password == password2:  # checking if 2 passwords are equal
            # encrypt before saving
            user.user_password = hash_password(password)
            user.save()

            return JsonResponse("Password reset successfully", safe=False, status=200)
        else:
            return JsonResponse("Passwords don't match.", safe=False, status=400)

    except Exception as e:
        logger.error(e)
        return JsonResponse("Error reset password function", safe=False, status=400)
