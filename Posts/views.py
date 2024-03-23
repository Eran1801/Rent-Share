from datetime import datetime
import traceback
from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
from Inbox.models import UserInbox
from Inbox.msg_emails_Enum import Emails
from Inbox.views import extract_message_based_on_confirm_status
from Posts.serializers import PostSerializerAll
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from .models import Post
from Users.utilities import *
from Posts.utilities import *
from django.core.exceptions import ObjectDoesNotExist
from Users.utilities import send_email
from datetime import datetime


# Define the logger at the module level
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

EMAIL_SUBJECT = 'New Post'


@api_view(['POST'])
@csrf_exempt
def add_post(request):

    try:
        data = request.data
        post_data = extract_post_data(data)

        post = PostSerializerAll(data=post_data, partial=True)

        if post.is_valid():

            saved_post = post.save()

            if isinstance(saved_post,Post):
                
                user = data.get('user')
                user_id = user.get('user_id')
                user_name = user.get('user_full_name')
                
                headline,message = extract_message_based_on_confirm_status(user_name,'0') # 0 means not confirmed yet
                
                # create a new value in Inbox table for this user with the right message and post_id
                UserInbox.objects.create(user_id=user_id,post_id=saved_post.post_id,user_message=message,headline=headline)
            
                # send email to the company email that a new post was added
                msg_html = Emails.NEW_POST_SEND_TO_ADMIN.value
                                
                # send an email for ourself for tracking the posts insertion and approval by the admin
                send_email(FROM_EMAIL, FROM_EMAIL, msg_html, EMAIL_SUBJECT)
                
                post.save() # save to db
                return JsonResponse("Post successfully saved in db", safe=False)
                                
        else:
            logger.info(post.errors)
            return HttpResponseServerError("Post validation failed")

    except Exception as e:
        # Log the full traceback along with the exception message
        logger.error(f"An error occurred in add_post: {e}\n{traceback.format_exc()}")
        return HttpResponseServerError('An error occurred while adding a new post')
    

@api_view(['GET'])
@csrf_exempt
def get_all_posts(request):
    """This function will be used to get all the posts in the db 'Posts'"""
    try:
        # extract all the posts from the db
        all_posts = Post.objects.all()
        all_posts_serialize = PostSerializerAll(all_posts,many=True) # many -> many posts

        return JsonResponse(all_posts_serialize.data, safe=False)

    except Exception as e:
         logger.error(f"get_all_posts : {e}")
         return HttpResponseServerError("An error occurred during get_all_posts")


@api_view(['GET'])
@csrf_exempt
def get_post_by_parm(request):
    # HERE - MORE CHECKS NEED TO BE CHECKS IN POSTMAN 
    """This function will be used to get the posts by the parameters that the user will send"""

    try:
        # extract values from the user request
        city, street, building_number, apartment_number = extract_fields_for_post_parm(request)
                
        # Validate the parameters
        validation_error = validate_post_parameters(city, street, building_number, apartment_number)
        if validation_error:
            return JsonResponse(validation_error, safe=False, status=400)

        # create the filter conditions before extract the right posts from db
        filter_conditions = filter_cond(city,street,building_number,apartment_number)
        
        # extract the posts that fill the filter_conditions
        post = Post.objects.filter(**filter_conditions)

        if post.exists():
            try:
                post_serializer = PostSerializerAll(post, many=True)

                # if more then one post for the same address we combined them to make it easy to the frontend
                if len(post_serializer.data) > 1:
                    apartments = process_apartments(post_serializer.data)
                    grouped_apartments = group_apartments_by_location(apartments) 
                    json_result = convert_to_json(grouped_apartments)

                    return JsonResponse(json_result, safe=False)
                
                return JsonResponse(post_serializer.data, safe=False)
            except :
                return HttpResponseServerError("An error occurred while serialize the post in get_posts")
        else:
            return HttpResponseNotFound("Post not found")

    except Exception as e:
         logger.error(f"get_posts : {e}")
         return HttpResponseServerError("An error occurred get_posts")


@api_view(['GET'])
@csrf_exempt
def get_post_by_post_id(request):

    try:
        post_id = request.GET.get('post_id')

        post = Post.objects.get(post_id=post_id) # get the post using post_id
        post_serializer = PostSerializerAll(post)

        return JsonResponse(post_serializer.data, safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred get_post_by_id: {e}")


@api_view(['GET'])
@csrf_exempt
def get_post_by_user_id(request):
    '''This function will be used to get all the posts (one or more) by the user ID for the "הדירות שלי"'''
    try:
        user_id = request.GET.get('user_id')

        posts = Post.objects.filter(post_user_id=user_id)
        post_serializer = PostSerializerAll(posts, many=True)

        return JsonResponse(post_serializer.data, safe=False)
    
    except Post.DoesNotExist:    
            return HttpResponseBadRequest("Post with the given ID does not exist.")
        
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")


@api_view(['PUT'])
@csrf_exempt
def update_description_post(request):
    '''This function will be used to update the description of a post'''
    try:
        data = request.data

        post_id = data.get('post_id')
        post_description = data.get('post_description')
    
        post = Post.objects.get(post_id=post_id)

        if post.post_description == post_description:
            return JsonResponse("The description is the same", safe=False)
        else: 
            # change the value in the db
            post.post_description = post_description

             # because he changed it, admin needs to approve
            post.confirmation_status = '0'

            post.save()

             # email to company mail to notice the change
            send_email(FROM_EMAIL,FROM_EMAIL,f"User : {post.post_user_id}\nPost : {post_id}\ndescription has changed","Post description changed")

            return JsonResponse("Description info updated successfully", safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest("An error occurred update_description_post")


@api_view(['DELETE'])
@csrf_exempt
def delete_post(request):
    '''This function will be used to delete a post'''
    try:
        post_id = request.GET.get('post_id')
        post = Post.objects.get(post_id=post_id)

        post.delete() # delete the post

        return JsonResponse("Post successfully deleted", safe=False)
    
    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest("An error occurred during delete_post")


@api_view(['GET'])
@csrf_exempt
def get_all_posts_zero_status(request):
    '''
    This function will be used to get all the posts in the db 'Posts'
    but only the posts with confirmation_status = '0'
    '''
    try:
        posts = Post.objects.filter(confirmation_status='0') # 0 means not confirmed yet
        post_serialize = PostSerializerAll(posts, many=True)

        return JsonResponse(post_serialize.data, safe=False)
    
    except ObjectDoesNotExist as e:
        logger.error(e)
        return HttpResponseServerError('Post not found')

    except Exception as e:
        return HttpResponseServerError("An error occurred during get_posts_excluding_confirmed")
    
    
@api_view(['PUT'])
@csrf_exempt
def update_post_for_approval(request):
    '''Update post is needed when there is a problem with the input of the user like id, address..'''
    try:
        # getting all the data of the post
        post_data = request.data
        post_id = post_data.get('post_id')
        
        # extract the post needs to be update
        post_to_update = Post.objects.get(post_id=post_id)

        # confirm_status is already change in the dashboard admin by us. when changes 'change_confirm_status()' is executed
        confirm_status = post_data.get('confirmation_status')

        switch_dict = {
            "2": update_post_address(post_to_update, post_data),
            "3": update_post_rent_dates(post_to_update, post_data),
            "4": update_post_rent_agreement(post_to_update, post_data),
            "5": update_post_driving_license(post_to_update, post_data)
        }

        response = switch_dict.get(confirm_status, "Invalid confirm status")
        if response == "Invalid confirm status":
            return HttpResponseBadRequest("Invalid confirm status")

        post_to_update.confirmation_status = '0' # needs to approve again by the admin
        post_to_update.save()

        return JsonResponse('Success to update the post',safe=False)

    except Post.DoesNotExist:
        logger.error('Post not found from update_post() ')
        return HttpResponseServerError("An error occurred during update_post()")

    except Exception as e:
        logger.error(e)
        return HttpResponseServerError("An error occurred during update_post()")


@api_view(['PUT'])
@csrf_exempt
def update_aprtemanet_pics(request):

    try:
        post_data = request.data

        post_id = post_data.get('post_id')
        post_to_update = Post.objects.get(post_id=post_id)

        max_pics = 4
        for i in range(max_pics):
            pic_base64 = post_data.get(f'apartment_pic_{i+1}')
            if pic_base64 is not None:
                content_file = convert_base64(pic_base64, f"apartment_pic_{i+1}")
                if content_file is not None:  # check if the return value is valid
                    setattr(post_to_update, f'apartment_pic_{i+1}', content_file)
        
        post_to_update.save()
        
        return JsonResponse('update_aprtemanet_pics end successfully',safe=False)

    except ObjectDoesNotExist as e:
        logger.error(f'post dont exists {e}')
        return HttpResponseBadRequest('Post dont exists')
    
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('something is wrong in the update_aprtemanet_pics')