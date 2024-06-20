from Inbox.msg_emails_Enum import Messages
from Posts.models import Post
import logging
from django.db import transaction


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def update_confirm_status_in_post(post_id, new_confirm_status):
    '''Update the confirmation_status field of a post'''
    try:
        post = Post.objects.get(post_id=post_id)
        post.confirmation_status = new_confirm_status
        
        with transaction.atomic():
            post.save()

        logger.info(f"Post {post_id} updated successfully")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist")

    except Exception as e:
        logger.error(f"An error occurred while updating post {post_id}: {e}") 



def extract_message_based_on_confirm_status(user_name,confirm_status:str):
    '''
    This function extract the right message and the heading of it 
    according to the confirm_status was givin
    the confirm_status is the status of the post after the user submitted it when 
    the admin need to approve it.'''

    # The dictionary contains the message and the heading for each confirmation status
    messages = {
        "0": [Messages.MESSAGE_0.value % user_name, 'תודה ששיתפת, מחכה לאישור'],
        "1": [Messages.MESSAGE_1.value % user_name, 'חוות דעתך אושרה'],
        "2": [Messages.MESSAGE_2.value % user_name, 'תיקון נדרש: בעיה בפרטי דירתך'],
        "3": [Messages.MESSAGE_3.value % user_name, 'בדוק תאריכים: תיקון נדרש בחוות דעתך'],
        "4": [Messages.MESSAGE_4.value % user_name, 'הגשה מחדש נדרשת: אי התאמה במסמכים'],
        "5": [Messages.MESSAGE_5.value % user_name, 'תיקון פרטים: אי התאמה בתעודה מזהה'],
        "6": [Messages.MESSAGE_6.value % user_name, 'עדכון נדרש: שפה לא נאותה בחוות הדעת']
    }

    return messages.get(confirm_status)[1], messages.get(confirm_status)[0]