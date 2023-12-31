from django.http import HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
from Users.models import Users
from .models import UserInbox
from Posts.models import Post
import logging
from .serializers import UserInboxSerializerAll

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
        confirm_status = data.get('confirm_status')
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        logger.info(f'cofirm_status = {confirm_status}')
        logger.info(f'user_id = {user_id}')
        logger.info(f'post_id = {post_id}')

        # update in 'Post' db the confirm status var
        post_to_update = Post.objects.get(post_id=post_id)
        post_to_update.confirmation_status = confirm_status

        logger.info(f'post_to_update.confirmation_status = {post_to_update.confirmation_status}')

        # extract the needed values for the message
        post_city = post_to_update.post_city
        post_street = post_to_update.post_street
        post_bulding_number = post_to_update.post_building_number
        post_apr_number = post_to_update.post_apartment_number

        post_to_update.save() # save the changes after extract and update the right values.

        # extract the needed value of user_name for the message
        user_name = Users.objects.get(user_id=user_id).user_full_name

        logger.info(f'user name = {user_name}')

        # extract the right message according to the confirm_status value
        message = confirmation_status_messages(user_name,post_city,post_street,post_bulding_number,post_apr_number,confirm_status)

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
        
        messages = UserInbox.objects.filter(user_id=user_id)
        messages_serlizer = UserInboxSerializerAll(messages,many=True)
        return JsonResponse(messages_serlizer.data, safe=False)
    
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError('An error occurred during get_all_user_messages')





