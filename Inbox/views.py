from collections import defaultdict
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
from Users.auth.decorators import jwt_required
from Users.models import Users
from Users.utilities import error_response, success_response
from .models import UserInbox
from Inbox.utilities import *
import logging
from .serializers import UserInboxSerializer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['GET'])
@csrf_exempt
@jwt_required
def get_all_user_messages(request):
    '''This function will activate when the user will enter the section of 'My Messages' '''
    try:
        user = Users.objects.get(user_id=request.user_id)
        messages = user.messages.all()  # I can use the messages because I establish it in the related_name in the ForeignKey.

        messages_serializer = UserInboxSerializer(messages, many=True)
        messages_data = messages_serializer.data

        # Group messages by post_id
        grouped_messages = defaultdict(list)
        for message in messages_data:
            grouped_messages[message['post_id']].append(message)

        # Convert to the desired format
        grouped_messages_list = [
            {"post_id": post_id, "messages": msgs}
            for post_id, msgs in grouped_messages.items()
        ]

        return success_response(data=grouped_messages_list, message="Success")

    except Users.DoesNotExist:
        return error_response('Message not found')

    except Exception as e:
        logger.error(e)
        return error_response('An error occurred during get_all_user_messages')


@api_view(['PUT'])
@csrf_exempt
@jwt_required
def update_read_status(request):
    try:
        messages_id = request.data.get('message_id')
        messages = UserInbox.objects.get(message_id=messages_id)
            
        messages.read_status = "1"
        with transaction.atomic():
            messages.save()

        return success_response('Update read status ends successful')

    except UserInbox.DoesNotExist as e:
        return error_response('UserInbox not found inside')
    
    except Exception as e:
        return error_response(f'Something went wrong inside update_read_status, {str(e)}')


@api_view(['DELETE'])
@csrf_exempt
@jwt_required
def delete_messages_by_post_id(request):
    try:

        post_id = request.data.get('post_id')
        
        # store all the messages with the same post_id
        message_to_delete = UserInbox.objects.filter(post_id=post_id)

        # delete all the messages of a post from db with the same post_id
        message_to_delete.delete()

        return success_response('delete_messages_by_post_id function end successfully')

    except UserInbox.DoesNotExist:
        return error_response('UserInbox not found inside delete_messages_by_post_id')
    
    except Exception as e:
        logger.error(e)
        return error_response('Something went wrong inside delete_messages_by_post_id')

    
@api_view(['GET'])
@csrf_exempt
def has_unread_messages(request):
    """NEEDS TO CHECK WHERE IT'S USED"""
    try:
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id)

        messages = user.messages.all() # get's all user messages

        # store all the messages that already read  
        unread_messages = extract_unread_messages(messages)
        
        return success_response(data=unread_messages, message='all unread messages was extracted successfully')
        
    except UserInbox.DoesNotExist:
        return error_response('Message dont exist.')

    except Exception as e:
        logger.error(e)
        return error_response('Something is wrong with had_unread_messages')