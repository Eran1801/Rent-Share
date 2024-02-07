from Posts.models import Post
import logging
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

    except Exception as e:
        logger.error(f"An error occurred while updating post {post_id}: {e}") 

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
        "0": [message_0,'תודה ששיתפת, מחכה לאישור'],
        "1": [message_1,'חוות דעתך אושרה'],
        "2": [message_2,'תיקון נדרש: בעיה בפרטי דירתך'],
        "3": [message_3,'בדוק תאריכים: תיקון נדרש בחוות דעתך'],
        "4": [message_4,'הגשה מחדש נדרשת: אי התאמה במסמכים'],
        "5": [message_5,'תיקון פרטים: אי התאמה בתעודה מזהה'],
        "6": [message_6,'עדכון נדרש: שפה לא נאותה בחוות הדעת']
    }

    return confirmation_status_messages.get(confirm_status)[0], confirmation_status_messages.get(confirm_status)[1]

