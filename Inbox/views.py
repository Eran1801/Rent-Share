from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
from Posts.serializers import PostSerializerAll
from Users.models import Users
from .models import UserInbox
from Posts.models import Post
from Inbox.utilities import *
import logging
from .serializers import UserInboxSerializerAll

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(["POST"])
@csrf_exempt
def update_confirm_status_field(request):

    try:
        data = request.data
        
        confirmation_status = data.get('confirmation_status')
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        # update in 'Post' db the confirm status var
        update_confirm_status_in_post(post_id,confirmation_status)

        # extract the needed value of user_name for the message
        user_name = Users.objects.get(user_id=user_id).user_full_name

        # extract the right message according to the confirm_status value
        message, headline = extract_message_based_on_confirm_status(user_name, confirmation_status)

        logger.info(f'message = {message}')

        # Add a message to the 'UserInbox' user db 
        UserInbox.objects.create(user_id=user_id,post_id=post_id,user_message=message,headline=headline)
        return JsonResponse('update_confirm_status end successfully',safe=False)

    except Exception as e:
        logger.error(f'Error: {e}')
        return HttpResponseServerError("An error occurred during update_confirm_status")


@api_view(['GET'])
@csrf_exempt
def get_all_user_messages(request):
    '''This function will activate when the user will enter the section of 'My Messages' '''
    try:
        user_id = request.GET.get('user_id')
        
        user = Users.objects.get(user_id=user_id)
        messages = user.messages.all() # i can use the messages because i establish it in the related_name in the forgien key.

        messages_serializer = UserInboxSerializerAll(messages,many=True)
        return JsonResponse(messages_serializer.data, safe=False)
    
    except Users.DoesNotExist:
        return HttpResponseServerError('Message not found')

    except Exception as e:
        logger.error(e)
        return HttpResponseServerError('An error occurred during get_all_user_messages')


@api_view(['PUT'])
@csrf_exempt
def update_read_status(request):
    try:
        data = request.data

        messages_id: list = data.get('messages_id')
                
        for _id in messages_id:
            messages = UserInbox.objects.get(message_id=_id)
            if messages.read_status == '1':
                continue
            
            messages.read_status = 1
            messages.save()

        return JsonResponse('update_read_status() end successful',safe=False)

    except UserInbox.DoesNotExist as e:
        logger.error(e)
        return HttpResponseBadRequest('UserInbox not found inside update_read_status')
    
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('Something wont wrong inside update_read_status')


@api_view(['DELETE'])
@csrf_exempt
def delete_messages_by_post_id(request):
    try:

        post_id = request.GET.get('post_id')
        
        # store all the messages with the same post_id
        message_to_delete = UserInbox.objects.filter(post_id=post_id)

        # delete all the post from db with the same post_id
        message_to_delete.delete()

        return JsonResponse('delete_messages_by_post_id function end successfully',safe=False)

    except UserInbox.DoesNotExist:
        return HttpResponseBadRequest('UserInbox not found inside delete_messages_by_post_id')
    
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('Something wont wrong inside delete_messages_by_post_id')

    
@api_view(['GET'])
@csrf_exempt
def has_unread_messages(request):
    try:
        user_id = request.GET.get('user_id')
        user = Users.objects.get(user_id=user_id)

        messages = user.messages.all() # get's all user messages

        # store all the messages that already reded  
        has_unread = any(mes.read_status == 1 for mes in messages)
        
        return JsonResponse({'unread_messages': has_unread},safe=False)
        
    except UserInbox.DoesNotExist:
        return HttpResponseBadRequest('Message dont exist.')

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('Something is wrong with had_unread_messages')


@api_view(['GET'])
@csrf_exempt
def get_all_messages_by_user_id(request):
    try:
        user_id = request.GET.get('user_id')

        # get all the messages of the user
        user = Users.objects.get(user_id=user_id)
        all_messages = user.messages.all()

        # flatten the resulting
        unique_post_ids = all_messages.values_list('post_id', flat=True).distinct()

        posts_data = normalize_messages(unique_post_ids)
        
        return JsonResponse({'posts': posts_data}, safe=False)
    
    except Post.DoesNotExist:
        return HttpResponseBadRequest('Post not found !')

    except UserInbox.DoesNotExist:
        return HttpResponseBadRequest('Message not found !')

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('something wont wrong in all_messages_by_post_id')


