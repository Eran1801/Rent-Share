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

def confirmation_status_messages(user_name,key:str):

    confirmation_status_messages = {
    "0": f"שלום {user_name} \nחוות הדעת שלך התקבלה אצלנו וממתינה לאישור.\nהודעה נוספת תישלח אלייך במידה וחוות הדעת תאושר.\nתוכל גם להתעדכן בסטטוס שלה באיזור \"הדירות שלי.\"",
    "1": f"שלום {user_name} \nחוות הדעת שלך אושרה.\nתודה רבה על תרומתך לקהילה.\nעכשיו תוכל למצוא אותה באזור חיפוש הדירות.",
    "2": f"שלום {user_name} \nזיהינו אי התאמה בין פרטי הדירה (עיר / רחוב / מספר בניין / דירה) לבין חוזה השכירות.\nאנא הוסף שנית את חוות הדעת עם הפרטים הנכונים.",
    "3": f"שלום {user_name} \nזיהינו אי התאמה בין תאריכי הכניסה והיציאה שהזנת לבין מה שרשום בחוזה השכירות.\nאנא הגש את חוות הדעת מחדש עם הפרטים הנכונים.",
    "4": f"שלום {user_name} \nזיהינו אי התאמה בין העלאת הטופס אשר עוזר לנו לאמת שאכן השכרת את הדירה (חוזה שכירות / חשבון חשמל / חשבון ארנונה).\nאנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים.",
    "5": f"שלום {user_name} \nזיהינו אי התאמה בין הפרטים בתעודה מזהה שהועלתה בחוות הדעת לבין חוזה השכירו.\nאנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים.",
    "6": f"שלום {user_name} \nזיהינו שפה לא נאותה במתן חוות הדעת שלך.\nאנא היכנס ל\"דירות שלי\" ועדכן את חוות הדעת על ידי שינוי המלל בתיבת הטקסט ולחיצה על כפתור \"עדכן חוות דעת\""
    }

    return confirmation_status_messages.get(key)

@api_view(["POST"])
@csrf_exempt
def update_confirm_status(request):

    try:
        data = request.data
        confirm_status = data.get('confirm_status')
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        # update in 'Post' db the confirm status value
        post_to_update = Post.objects.filter(post_id=post_id)
        post_to_update.update(confirmation_status=confirm_status)

        user_name = Users.objects.get(user_id=user_id).user_full_name
        # extract the right message according to the confirm_status value
        message = confirmation_status_messages(user_name,confirm_status)

        # Add a message to the 'UserInbox' user db 
        UserInbox.create(user_id=user_id,post_id=post_id,user_message=message)
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
        
        messages = UserInbox.objects.filter(user_id=user_id)
        messages_serlizer = UserInboxSerializerAll(messages,many=True)
        return JsonResponse(messages_serlizer.data, safe=False)
    
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError('An error occurred during get_all_user_messages')





