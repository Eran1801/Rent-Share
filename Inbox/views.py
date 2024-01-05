from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
from Users.models import Users
from .models import UserInbox
from Posts.models import Post
import logging
from .serializers import UserInboxSerializerAll
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def update_confirm_status_in_post(post_id, new_confirm_status) -> Post:
    '''Update the confirmation status and post_to_update field of a post.'''
    try:
        post = Post.objects.get(post_id=post_id)
        post.confirmation_status = new_confirm_status
        post.save()

        logger.info(f"Post {post_id} updated successfully.")
        return post
    
    except ObjectDoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
        return HttpResponseServerError('An error occurred while adding a new post')

    except Exception as e:
        logger.error(f"An error occurred while updating post {post_id}: {e}") 
        return HttpResponseServerError('An error occurred while adding a new post')


    # if post not found
    return None


def confirmation_status_messages(user_name,confirm_status):
    '''This function extract the right message according to the confirm_status was givin'''

    message_0 = (
        f"שלום {user_name} \n"
        "חוות הדעת שלך התקבלה אצלנו וממתינה לאישור.\n"
        "הודעה נוספת תישלח אלייך במידה וחוות הדעת תאושר.\n"
        "תוכל גם להתעדכן בסטטוס שלה באיזור \"הדירות שלי.\""
    )

    message_1 = (
        f"שלום {user_name} \n"
        "חוות הדעת שלך אושרה.\n"
        "תודה רבה על תרומתך לקהילה.\n"
        "עכשיו תוכל למצוא אותה באזור חיפוש הדירות."
    )

    message_2 = (
        f"שלום {user_name} \n"
        "זיהינו אי התאמה בין פרטי הדירה (עיר / רחוב / מספר בניין / דירה) לבין חוזה השכירות.\n"
        "אנא הוסף שנית את חוות הדעת עם הפרטים הנכונים."
    )

    message_3 = (
        f"שלום {user_name} \n"
        "זיהינו אי התאמה בין תאריכי הכניסה והיציאה שהזנת לבין מה שרשום בחוזה השכירות.\n"
        "אנא הגש את חוות הדעת מחדש עם הפרטים הנכונים."
    )

    message_4 = (
        f"שלום {user_name} \n"
        "זיהינו אי התאמה בין העלאת הטופס אשר עוזר לנו לאמת שאכן השכרת את הדירה (חוזה שכירות / חשבון חשמל / חשבון ארנונה).\n"
        "אנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים."
    )

    message_5 = (
        f"שלום {user_name} \n"
        "זיהינו אי התאמה בין הפרטים בתעודה מזהה שהועלתה בחוות הדעת לבין חוזה השכירו.\n"
        "אנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים."
    )

    message_6 = (
        f"שלום {user_name} \n"
        "זיהינו שפה לא נאותה במתן חוות הדעת שלך.\n"
        "אנא היכנס ל\"דירות שלי\" ועדכן את חוות הדעת על ידי שינוי המלל בתיבת הטקסט ולחיצה על כפתור \"עדכן חוות דעת\"."
    )

    confirmation_status_messages = {
        "0": message_0,
        "1": message_1,
        "2": message_2,
        "3": message_3,
        "4": message_4,
        "5": message_5,
        "6": message_6
    }

    return confirmation_status_messages.get(confirm_status)


@api_view(["POST"])
@csrf_exempt
def update_confirm_status(request):

    try:
        data = request.data
        
        confirmation_status = data.get('confirmation_status')
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        logger.info(f'confirmation_status = {confirmation_status}')
        logger.info(f'user_id = {user_id}')
        logger.info(f'post_id = {post_id}')

        # update in 'Post' db the confirm status var
        post_to_update = update_confirm_status_in_post(post_id,confirmation_status)

        logger.info(f'post_to_update.confirmation_status = {post_to_update.confirmation_status}')

        # extract the needed value of user_name for the message
        user_name = Users.objects.get(user_id=user_id).user_full_name

        logger.info(f'user name = {user_name}')

        # extract the right message according to the confirm_status value
        message = confirmation_status_messages(user_name, confirmation_status)

        logger.info(f'message = {message}')

        # Add a message to the 'UserInbox' user db 
        UserInbox.objects.create(user_id=user_id,post_id=post_id,user_message=message)
        return JsonResponse('update_confirm_status end successfuly',safe=False)

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during update_confirm_status")


@api_view(['GET'])
@csrf_exempt
def get_all_user_messages(request):
    '''This function will activate when the user will enter the section of 'My Messages' '''
    try:
        user_id = request.GET.get('user_id')
        logger.info(f'user_id = {user_id}')
        
        user = Users.objects.get(user_id=user_id)
        messages = user.messages.all() # i can use the messages bceause i estblish it in the related_name in the forg key.

        logger.info(f'messages - {messages} and len = {len(messages)}')

        messages_serlizer = UserInboxSerializerAll(messages,many=True)
        return JsonResponse(messages_serlizer.data, safe=False)
    
    except ObjectDoesNotExist:
        return HttpResponseServerError('Message not found')

    except Exception as e:
        logger.error(e)
        return HttpResponseServerError('An error occurred during get_all_user_messages')


@api_view(['PUT'])
@csrf_exempt
def update_read_status(request):
    try:
        data = request.data

        message_id = data.get('message_id')
        message_to_update = UserInbox.objects.get(message_id=message_id)
        message_to_update.read_status = '1'

        message_to_update.save()

        return JsonResponse('update_read_status() end succsufuly',safe=False)

    except UserInbox.DoesNotExist as e:
        logger.error(e)
        return HttpResponseBadRequest('UserInbox not found inisde update_read_status')
    
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('Something wont wrong inside update_read_status')


@api_view(['DELETE'])
@csrf_exempt
def delete_message(request):
    try:

        message_id = request.GET.get('message_id')
        logger.info(f'message_id - {message_id}')

        message_to_update = UserInbox.objects.get(message_id=message_id)
        message_to_update.delete()

        return JsonResponse('delete_message() end succsufuly',safe=False)

    except UserInbox.DoesNotExist as e:
        logger.error(e)
        return HttpResponseBadRequest('UserInbox not found inisde delete_message')
    
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('Something wont wrong inside delete_message')

    



