from Inbox.models import UserInbox
from Inbox.msg_emails_Enum import Messages
from Inbox.serializers import UserInboxSerializerAll
from Posts.models import Post
import logging

from Posts.serializers import PostSerializerAll

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def extract_unread_messages(messages) -> dict:
    '''Extract the unread messages from a list of messages'''
    ans = {}
    
    for mes in messages:
        if mes.read_status == '1':
            if mes.post_id not in ans:
                ans[mes.post_id] = []
                ans[mes.post_id].append((mes.user_message, mes.headline))
            else:
                ans[mes.post_id].append((mes.user_message, mes.headline))
    
    return ans

def update_confirm_status_in_post(post_id, new_confirm_status) -> Post:
    '''Update the confirmation_status field of a post'''
    try:
        post = Post.objects.get(post_id=post_id)
        post.confirmation_status = new_confirm_status
        post.save()

        logger.info(f"Post {post_id} updated successfully.")
        return post
    
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")

    except Exception as e:
        logger.error(f"An error occurred while updating post {post_id}: {e}") 

    # if post not found
    return None


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


def normalize_messages(unique_post_ids):
    
    try:
        posts_data = []
        # for each post_id in the list of unique post_ids
        for post_id in unique_post_ids:
            # get the post object
            post = Post.objects.get(post_id=post_id) 

            # convert post to a dict for JSON response
            post_dict = {"post": PostSerializerAll(post).data}

            # get's all the messages that associated to this post_id and order them by message_id as the message id is the order of the messages
            all_post_messages = UserInbox.objects.filter(post_id=post_id).order_by('message_id')

            # sorted the message inside a list for the JSON return
            message_list_sorted = [mes.user_message for mes in all_post_messages]
            post_dict['messages_sorted'] = message_list_sorted

            # the actual messages in a dict form for the JSON return
            post_dict['massages'] = UserInboxSerializerAll(all_post_messages,many=True).data
        
            posts_data.append(post_dict)

        return posts_data
    
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    
    except Exception as e:
        logger.error(f"An error occurred while normalizing messages for post {post_id}: {e}")