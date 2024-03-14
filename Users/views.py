from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from django.http import *
from rest_framework.decorators import api_view
from Posts.views import convert_base64
from Users.models import Users
from Users.serializers import UserSerializerPicture, UsersSerializer
from Users.utilities import *
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@api_view(['POST'])
@csrf_exempt
def register(request, user_id = 0): 

    try:
        user_data = request.data 
        
        # extract data
        user_full_name = user_data.get('user_full_name')
        user_email = user_data.get('user_email').lower() # lower case email
        user_phone_number = user_data.get('user_phone')
        user_password = user_data.get('user_password')
        user_password_2 = user_data.get('user_password_2')

        # checks valid register input from user
        check_full_name: bool = full_name_check(user_full_name)
        check_phone_number = phone_number_check(user_phone_number)
        check_password = check_valid_password(user_password)

        if user_password == user_password_2: # checking if 2 user passwords are equal

            # return associated error message if the input is invalid
            if check_full_name is False:
                return HttpResponseServerError('Invalid full name')

            if email_exists(user_email) is True: 
                return HttpResponseServerError('Email already exists')
            
            if phone_exists(user_phone_number) is True:
                return HttpResponseServerError('Phone number already exists')
            
            if check_phone_number is False:
                return HttpResponseServerError('Invalid phone number')
            
            if check_password is False:
                return HttpResponseServerError('Invalid password')

            del user_data['user_password_2'] # don't needs to be save in the db after checking
            user_data['user_password'] = hash_password(user_password) # encrypt before saving

            users_serializer = UsersSerializer(data=user_data)
            if users_serializer.is_valid():
                users_serializer.save() # save to db
                return JsonResponse("Register Success",safe=False)
            else:
                logger.debug(users_serializer.errors)
                return HttpResponseServerError("Register Fails")
        else:
            return HttpResponseServerError("Passwords don't match.")
            
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error in register function")
    

@api_view(['POST'])
@csrf_exempt
def login(request):

    try:
        user_data = request.data

        # extract the right data
        login_email_address = user_data.get('user_email').lower() # lower case email 
        login_password = user_data.get('user_password')

        # encrypt user password for check similarity in the db
        hash_password_login = hash_password(login_password) 

        # retrieve user from db based on email
        user = Users.objects.get(user_email=login_email_address)

        if user.user_password == hash_password_login:
            
            # sending to the frontend
            response_data = {
            'user': {
                'user_id': user.user_id,
                'user_full_name': user.user_full_name,
                'user_email': user.user_email,
                'user_phone': user.user_phone
            },
                'message': 'Passwords match. Login successfully'
            }
            
            return JsonResponse(response_data)
        else:
            return HttpResponseServerError("Passwords Incorrect. Login fail")
        
    except Users.DoesNotExist:
        return HttpResponseServerError("Email don't exists. Login fail")
    
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error in login function")


@api_view(['DELETE'])
@csrf_exempt    
def delete_user(request):

    try:
        # get operation diff in extract data
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id) # from db

        # delete user, posts, messages from db
        user.delete() 

        return JsonResponse('Delete successfully', safe=False)
    
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error deleting user function")


@api_view(['GET'])
@csrf_exempt
def forget_password(request):
    try:
        
        # extract the user email
        user_email = request.GET.get('user_email').lower() # lower case email

        # first check if the email is in the db, if the user doesn't exist, return error
        if email_exists(user_email) is False:
            return HttpResponseServerError('Email dont exists')

        confirm_code = generate_random_digits()
        msg = f'קוד האימות שלך הוא : {confirm_code}\nהקוד תקף ל-5 דקות'
        subject = 'איפוס סיסמה'

        # send email to user email with a 6 digit code
        send_email_via_mailtrap("eranlevy9@gmail.com",user_email,msg,subject)
        
        response_data = {
            'user': {
                'user_email': user_email,
                'confirm_code': confirm_code,
            },
                'message': f"Email sent successfully with code : {confirm_code} with email {user_email}"
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        logger.error('Error forget password: %s', e)
        return HttpResponseServerError("Error forget password function")
    

@api_view(['PUT'])
@csrf_exempt
def reset_password(request):
    try:

        data = request.data

        # extract the right data
        user_email = data.get('user_email').lower() # lower case email
        user_password = data.get('user_password')
        user_password_2 = data.get('user_password_2')

        if check_valid_password(user_password) is False:
            return HttpResponseServerError("Password is invalid")

        if user_password == user_password_2: # checking if 2 user passwords are equal

            # retrieve user from db based on email
            user = Users.objects.get(user_email=user_email)

            # encrypt before saving
            user.user_password = hash_password(user_password) 

            user.save()

            return JsonResponse("Password reset successfully", safe=False)
        else:
            return HttpResponseServerError("Passwords don't match.")
        
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("Error reset password function")
    
# --- PERSONAL INFO SECTION --- 
    
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

        # check if fields have changed
        if full_name != user.user_full_name:
            if full_name_check(full_name) is False:
                return HttpResponseServerError("Invalid full name")
            else:
                user.user_full_name = full_name # changing the full name in the db

        # means it's diff from the record in the db
        if email != user.user_email:
            if email_exists(email) is True:
                return HttpResponseServerError("Email already exists")
            
            elif check_email_valid(email) is False:
                return HttpResponseServerError("Email is invalid")
            
            else:
                user.user_email = email

        if phone != user.user_phone:
            if phone_exists(phone) is True:
                return HttpResponseServerError("Phone number already exists")
            
            elif phone_number_check(phone) is False:
                return HttpResponseServerError("Phone number is invalid")
            
            else:
                user.user_phone = phone
        
        user.save()  # save changes to the database, but only the one's that the user changed
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
        user_id = user_data.get('user_id')

        # encrypt the old password for checking against the db
        old_password = hash_password(user_data.get('old_password'))

        new_password = user_data.get('new_password')
        new_password_confirm = user_data.get('new_password_confirm')

        user = Users.objects.get(user_id=user_id) # get the User from the database by user_id
        
        # check if the old password is correct
        if user.user_password != old_password:
            return HttpResponseServerError("Old password is incorrect")
        
        if new_password != new_password_confirm:
            return HttpResponseServerError("Passwords don't match.")
        
        if check_valid_password(new_password) is False:
            return HttpResponseServerError("Password is invalid")
        
        # update the password but encrypt is first
        user.user_password = hash_password(new_password)

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
    '''This function will be used to change the user's profile picture'''

    try:
        user_data = request.data
        user_id = user_data.get('user_id')

        profile_image_base64 = user_data.get('profile_image')
        profile_image_file = convert_base64(profile_image_base64, "profile_image")

        user = Users.objects.get(user_id=user_id) # get the user from the database by user_id

        data = {'user_profile_pic': profile_image_file}
       
        # serialize only the photo field that separates the image from the rest of the data
        user_serializer = UserSerializerPicture(instance=user, data=data, partial=True)
        
        if user_serializer.is_valid():
            user_serializer.save()  # attempt to save to the database
            logger.info("Saved to the database")
            return JsonResponse("Profile picture successfully saved in db", safe=False)
        
        else:
            logger.debug(user_serializer.errors)
            return HttpResponseServerError("An error occurred during profile picture upload")

    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")
    
    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during profile picture upload")
  
    
@api_view(['GET'])
@csrf_exempt
def get_profile_pic(request):
    try:
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id) # get the user from the database by user_id

        user_serializer = UserSerializerPicture(instance = user, many=False, partial=True)
        return JsonResponse(user_serializer.data, safe=False)
    
    except Users.DoesNotExist:
        return HttpResponseServerError("User not found")
    
    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during profile picture upload")
    