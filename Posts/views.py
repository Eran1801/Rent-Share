from datetime import datetime
from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
import logging
from Inbox.models import UserInbox
from Inbox.views import confirmation_status_messages
from Posts.serializers import PostSerializerAll
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from .models import Post
from Users.utilities import *
from Posts.utilities import *
from django.core.exceptions import ObjectDoesNotExist
from Users.utilities import send_email


# Define the logger at the module level
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['POST'])
@csrf_exempt
def add_post(request):

    try:
        post_data = request.data    

        # inside convert_images_to_files we extract the post data and convert the images to files
        post_data_dict = convert_images_to_files(post_data)

        post = PostSerializerAll(data=post_data_dict, partial=True)

        if post.is_valid():

            saved_post = post.save()

            if isinstance(saved_post,Post):

                # create a new value in Inbox table for this user with the right message and post_id
                user_name = post_data.get('user').get('user_full_name')

                message,headline = confirmation_status_messages(user_name,'0') # 0 means not confirmed yet

                user_id = post_data.get('user').get('user_id')
                UserInbox.objects.create(user_id=user_id,post_id=saved_post.post_id,user_message=message,headline=headline)

                # send email to the company email that a new post was added
                msg = f"New post was added to S3.\nUser : {post_data.get('user').get('user_id')}"
                subject = "New post"
                send_email_via_sendgrid(FROM_EMAIL, FROM_EMAIL, msg, subject)
                
                return JsonResponse("Post successfully saved in db", safe=False)
        else:
            logger.info(post.errors)
            return HttpResponseServerError("Post validation failed")

    except Exception as e:
        logger.error(f"add_post : {e}")
        return HttpResponseServerError('An error occurred while adding a new post')


@api_view(['GET'])
@csrf_exempt
def get_all_posts(request):

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

    try:
        # extract the right values from the user
        post_city = request.GET.get('post_city') 
        post_street = request.GET.get('post_street')
        post_building_number = request.GET.get('post_building_number')
        post_apartment_number = request.GET.get('post_apartment_number')

        # edge cases to check first        
        if post_city == '' and post_street == 'null' and post_apartment_number == 'null' and post_building_number == 'null': 
            return HttpResponseBadRequest("At least one field is required")

        # without city you can't search anything
        if post_city == '':
            return HttpResponseBadRequest("City field is required")

        # create the filter conditions before extract the right posts from db
        filter_conditions = filter_cond(post_city,post_street,post_building_number,post_apartment_number)

        # extract the posts that fill the filter_conditions
        post = Post.objects.filter(**filter_conditions)

        if post.exists():
            try:
                post_serializer = PostSerializerAll(post, many=True)

                # if more then one post for the same address we combined them to make it easy to the front
                apartments = process_apartments(post_serializer.data)
                grouped_apartments = group_apartments_by_location(apartments) 
                json_result = convert_to_json(grouped_apartments)

                return JsonResponse('{' + json_result + '}', safe=False)   
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
        posts = Post.objects.filter(confirmation_status='0')
        post_serialize = PostSerializerAll(posts, many=True)

        return JsonResponse(post_serialize.data, safe=False)
    
    except ObjectDoesNotExist as e:
        logger.error(e)
        return HttpResponseServerError('Post not found')

    except Exception as e:
        return HttpResponseServerError("An error occurred during get_posts_excluding_confirmed")
    
    
@api_view(['PUT'])
@csrf_exempt
def update_post(request):
    '''Update post is needed when there is a problem with the input of the user like id, address..'''
    try:
        # getting all the data of the post
        post_data = request.data
        logger.info(f'post_data = {post_data}')

        # extract the post needs to be update
        post_id = post_data.get('post_id')
        
        post_to_update = Post.objects.get(post_id=post_id)

        # confirm_status is already change in the dashboard admin by us. when changes 'change_confirm_status()' is executed
        confirm_status = post_data.get('confirmation_status')

        # switch case on the 'confirm_status' var
        if confirm_status == '2':
        
            post_to_update.post_city = post_data.get('post_city')
            post_to_update.post_street = post_data.get('post_street')
            post_to_update.post_building_number = post_data.get('post_building_number')
            post_to_update.post_apartment_number = post_data.get('post_apartment_number')

        elif confirm_status == '3':

            new_rent_start_date = post_data.get('post_rent_start')
            new_rent_end_date = post_data.get('post_rent_end')

            new_rent_start_date = datetime.strptime(new_rent_start_date, '%Y-%m-%d').date()
            new_rent_end_date = datetime.strptime(new_rent_end_date, '%Y-%m-%d').date()

            post_to_update.post_rent_start = new_rent_start_date
            post_to_update.post_rent_end = new_rent_end_date
        
        elif confirm_status == '4':

            rent_agreement_base64 = post_data.get('rent_agreement')
            new_rent_agreement = convert_base64(rent_agreement_base64, "new rent agreement")

            post_to_update.rent_agreement = new_rent_agreement
        
        elif confirm_status == '5':

            driving_license_base64 = post_data.get('driving_license')
            new_driving_license = convert_base64(driving_license_base64, "new driving license")

            post_to_update.driving_license = new_driving_license

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