from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
import Users
from Users.serializers import UserSerializerPicture
from Users.views import *
from Posts.views import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from Posts.models import Post
from .models import Inbox


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def confirmation_status_messages_dict(user_name):

    confirmation_status_messages = {
    "0": f"שלום {user_name} \nחוות הדעת שלך התקבלה אצלנו וממתינה לאישור.\nהודעה נוספת תישלח אלייך במידה וחוות הדעת תאושר.\nתוכל גם להתעדכן בסטטוס שלה באיזור \"הדירות שלי.\"",
    "1": f"שלום {user_name} \nחוות הדעת שלך אושרה.\nתודה רבה על תרומתך לקהילה.\nעכשיו תוכל למצוא אותה באזור חיפוש הדירות.",
    "2": f"שלום {user_name} \nזיהינו אי התאמה בין פרטי הדירה (עיר / רחוב / מספר בניין / דירה) לבין חוזה השכירות.\nאנא הוסף שנית את חוות הדעת עם הפרטים הנכונים.",
    "3": f"שלום {user_name} \nזיהינו אי התאמה בין תאריכי הכניסה והיציאה שהזנת לבין מה שרשום בחוזה השכירות.\nאנא הגש את חוות הדעת מחדש עם הפרטים הנכונים.",
    "4": f"שלום {user_name} \nזיהינו אי התאמה בין העלאת הטופס אשר עוזר לנו לאמת שאכן השכרת את הדירה (חוזה שכירות / חשבון חשמל / חשבון ארנונה).\nאנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים.",
    "5": f"שלום {user_name} \nזיהינו אי התאמה בין הפרטים בתעודה מזהה שהועלתה בחוות הדעת לבין חוזה השכירו.\nאנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים.",
    "6": f"שלום {user_name} \nזיהינו שפה לא נאותה במתן חוות הדעת שלך.\nאנא היכנס ל\"דירות שלי\" ועדכן את חוות הדעת על ידי שינוי המלל בתיבת הטקסט ולחיצה על כפתור \"עדכן חוות דעת\""
    }

    return confirmation_status_messages


def adding_message_to_inbox(user_id,message,message_field):
    '''This function will be used to add a message to the user inbox'''
    try:  
        # get the Inbox instance for the given user_id
        inbox, created = Inbox.objects.get_or_create(user_id=user_id) # created = True if the object was created, False if it was retrieved from the database
        
        # Dynamically set the message to the specified field
        if hasattr(inbox, message_field):
            setattr(inbox, message_field, message)
            inbox.save()
        else:
            return HttpResponseServerError(f'Invalid field: {message_field}')

    except Exception as e:
        logger.error(f"adding_message_to_inbox: {e}")
        return HttpResponseServerError('An error occurred while adding message to inbox')
    

@receiver(post_save, sender=Post) # sender it from where the change will be made
def confirmation_status_update(sender, instance, created, **kwargs):
    if created is False:
        # returns a dictionary of fields that have changed since the model was last saved
        changed_fields = instance.get_dirty_fields()
        logger.info(f'Changed fields: {changed_fields}')

        if 'confirmation_status' in changed_fields:
            # get the user that made the change in the database
            user = Inbox.objects.get(user_id = instance.post_user_id)
            logger.info(f'User:{user}')

            # get the confirmation status of the post
            confirmation_status = changed_fields.get('confirmation_status')
            logger.info(f'Confirmation status: {confirmation_status}')

            message = confirmation_status_messages_dict(user.user_id).get(confirmation_status)
            logger.info(f'Message: {message}')

            message_field = f'user_message_{confirmation_status+1}'
            adding_message_to_inbox(user.user_id,message,message_field)

def check_email_valid(email:str)->bool:
    return True if email.count('@') == 1 or email.count('.') >= 1 else False
       

@api_view(['PUT'])
@csrf_exempt
def change_personal_info(request):
    '''This function will be used to change the user's personal info'''

    try:
        user_data = request.data

        user_id = user_data.get('user_id')
        full_name = user_data.get('user_full_name')
        phone = user_data.get('user_phone')
        email = user_data.get('user_email')
        
        user = Users.objects.get(user_id=user_id)  # Get the user from the database by user_id

        # Check if fields have changed
        if full_name != user.user_full_name:
            if not full_name_check(full_name):
                return HttpResponseServerError("Invalid full name")
            else:
                user.user_full_name = full_name # changing the 

        if email != user.user_email:
            if email_exists(email) == True:
                return HttpResponseServerError("Email already exists")
            elif check_email_valid(email):
                return HttpResponseServerError("Email is invalid")
            else:
                user.user_email = email

        if phone != user.user_phone:
            if phone_number_check(phone) == False:
                return HttpResponseServerError("Phone number is invalid")
            if phone_exists(phone) == True:
                return HttpResponseServerError("Phone number already exists")
            user.user_phone = phone
        
        user.save()  # save changes to the database, but only the one the user changed
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

        old_password = hash_password(user_data.get('old_password')) # encrypt the old password
        new_password = user_data.get('new_password')
        new_password_confirm = user_data.get('new_password_confirm')

        user = Users.objects.get(user_id=user_data.get('user_id')) # get the user from the database by user_id
        
        # check if the old password is correct
        if user.user_password != old_password:
            return HttpResponseServerError("Old password is incorrect")
        
        if new_password != new_password_confirm:
            return HttpResponseServerError("Passwords don't match.")
        
        if check_valid_password(new_password) == False:
            return HttpResponseServerError("Password is invalid")
        
        user.user_password = hash_password(new_password) # update the password
        user.save() # save changes to the database

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

        profile_image_base64 = user_data.get('profile_image')  # Extract the first item from the list
        profile_image_file = convert_base64(profile_image_base64, "profile_image")

        user = Users.objects.get(user_id=user_id) # get the user from the database by user_id

        data = {'user_profile_pic': profile_image_file}
       
        # serialize only the photo field that separates the image from the rest of the data
        user_serializer = UserSerializerPicture(instance=user, data=data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()  # Attempt to save to the database
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
    