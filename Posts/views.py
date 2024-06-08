import os
from venv import logger
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.decorators import api_view
from Inbox.models import UserInbox
from Inbox.msg_emails_Enum import FROM_EMAIL, Emails
from Inbox.utilities import update_confirm_status_in_post
from Inbox.views import extract_message_based_on_confirm_status
from Posts.serializers import PostSerializer
from Posts.utilities import activate_function_based_on_status, convert_to_json, group_apartments_by_location, process_apartments
from Users.auth.decorators import jwt_required
from Users.models import Users
from .models import Post
from Users.utilities import error_response, send_email, success_response
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes


@api_view(['POST'])
@csrf_exempt
@jwt_required
@parser_classes([MultiPartParser, FormParser])
def add_post(request):

    try:
        user_id = request.user_id
        user = Users.objects.get(user_id=user_id)
        
        post = PostSerializer(data=request.data, partial=True)

        if post.is_valid():

            # save the user id that added the post
            post.validated_data['post_user_id'] = request.user_id
            with transaction.atomic():
                saved_post = post.save()

            if isinstance(saved_post, Post):
                
                user_full_name = user.user_full_name
                headline, message = extract_message_based_on_confirm_status(user_full_name, '0')  # 0 means not confirmed yet
                
                # create a new value in Inbox table for this user with the right message for creating a new post
                UserInbox.objects.create(user_id=request.user_id, post_id=saved_post.post_id, user_message=message, headline=headline)
            
                # # extract email message
                # msg_html = Emails.NEW_POST_SEND_TO_ADMIN.value
                                
                # # send an email for ourselves for tracking the posts insertion and approval by the admin
                # company_email = os.environ.get('COMPANY_EMAIL')
                # send_email(company_email, company_email, msg_html, Emails.EMAIL_NEW_POST_SUBJECT)
                
                return success_response("Post successfully saved in db")
                                
        return error_response(f"Post validation failed, {post.errors}")

    except Exception as e:
        return error_response(f'An error occurred while adding a new post, {e}')


@api_view(['GET'])
@csrf_exempt
def get_all_posts(request):
    """This function will be used to get all the posts in the db 'Posts'"""
    try:
        # extract all the posts from the db
        all_posts = Post.objects.all()
        all_posts_serialize = PostSerializer(all_posts, many=True)  # many -> many posts

        return success_response(data=all_posts_serialize.data,message="All posts retrieved successfully")

    except Exception as e:
         logger.error(f"get_all_posts : {e}")
         return error_response("An error occurred during get_all_posts")


@api_view(['GET'])
@csrf_exempt
@jwt_required
def get_post_by_parameters(request):
    """This function will be used to get the posts by the parameters that the user will send"""
    try:

        search_post = request.data.copy()
        search_post['confirmation_status'] = '1' # get only approved posts
                
        # extract the posts that fulfill the filter_conditions
        # post = Post.objects.filter(confirmation_status=1, post_city='עכו')
        post = Post.objects.filter(**search_post)

        if post.exists():
            post_serializer = PostSerializer(post, many=True)

            # # if more than one post for the same address we combine them to make it easy for the frontend to 
            # if len(post_serializer.data) > 1:
            #     apartments = process_apartments(post_serializer.data)
            #     grouped_apartments = group_apartments_by_location(apartments) 
            #     json_result = convert_to_json(grouped_apartments)
            
            return success_response(data=post_serializer.data, message="Post/s retrieved successfully")
        else:
            return error_response("Post not found")

    except Exception as e:
         return error_response(f"An error occurred get_posts, {e}")


@api_view(['GET'])
@csrf_exempt
@jwt_required
def get_post_by_post_id(request):

    try:
        post_id = request.GET.get('post_id')

        post = Post.objects.get(post_id=post_id)
        post_serializer = PostSerializer(post)

        return success_response(data=post_serializer.data, message="Post retrieved successfully")

    except Post.DoesNotExist:
            return error_response("Post with the given ID does not exist")
        
    except Exception as e:
            return error_response(f"An error occurred get_post_by_id: {e}")


@api_view(['GET'])
@csrf_exempt
@jwt_required
def get_all_user_posts(request):
    '''This function will be used to get all the posts (one or more) by the user ID for the "הדירות שלי"'''
    try:
        user_id = request.GET.get('user_id')

        posts = Post.objects.filter(post_user_id=user_id)
        post_serializer = PostSerializer(posts, many=True)

        return success_response(data=post_serializer.data, message="Post by user id retrieved successfully")
    
    except Post.DoesNotExist:    
            return error_response("Post with the given ID does not exist.")
        
    except Exception as e:
            return error_response(f"An error occurred: {e}")


@api_view(['PATCH'])
@csrf_exempt
@jwt_required
def update_post_review(request):
    '''This function will be used to update the review of a post'''
    try:
        
        post_id = request.data.get('post_id')
        new_post_review = request.data.get('post_review')
    
        post = Post.objects.get(post_id=post_id) # extract post

        if post.post_review == new_post_review: # check for changes 
            return success_response("Review is the same. no changes were made")
        
        # update review in db
        post.post_review = new_post_review

        # admin needs to approve again the review, so we change confirmation_status to '0'
        post.confirmation_status = '0'
        
        with transaction.atomic():
            post.save()

            #  # email to the company email to notice the change and approved the new review
            # company_mail = os.environ.get('COMPANY_EMAIL')
            # send_email(company_mail, company_mail,f"User : {post.post_user_id}\nPost : {post_id}\nreview has changed","Post description changed")

            return success_response("Post review updated successfully")

    except Post.DoesNotExist:
            return error_response("Post with the given ID does not exist")
        
    except Exception as e:
            return error_response(f"An error occurred update_description_post, {e}")


@api_view(['DELETE'])
@csrf_exempt
@jwt_required
def delete_post(request):
    '''This function will be used to delete a post'''
    try:
        post_id = request.GET.get('post_id')
        post = Post.objects.get(post_id=post_id)

        post.delete() # delete the post

        return success_response(f"Post with post id - {post_id} successfully deleted")
    
    except Post.DoesNotExist:
            return error_response("Post with the given ID does not exist")
        
    except Exception as e:
            return error_response(f"An error occurred during delete_post, {e}")


@api_view(['GET'])
@csrf_exempt
def get_unapproved_posts(request):
    '''
    This function will be used to get all the posts in the db 'Posts'
    but only the posts with confirmation_status = '0', means unapproved posts
    '''
    try:
        posts = Post.objects.filter(confirmation_status='0')  # 0 means not confirmed yet
        post_serialize = PostSerializer(posts, many=True)

        return success_response(data=post_serialize.data, message="All unapproved posts retrieved successfully")
    
    except Post.DoesNotExist:
        logger.error("Post does not exist")
        return error_response("There isn't posts that are unapproved")

    except Exception as e:
        return error_response(f"An error occurred during get_posts_excluding_confirmed {e}")


@api_view(["GET"])
@csrf_exempt
@jwt_required
def get_approved_posts(request):
    
    try:
        all_approved_posts = Post.objects.filter(confirmation_status='1')
        
        if all_approved_posts:
            all_approved_posts_ser = PostSerializer(all_approved_posts, many=True)
            return success_response(all_approved_posts_ser.data, "All approved posts retrieved successfully")
        
        else:
            return error_response("Not found approved posts")

    except Exception as e:
        return error_response(f'Something wont wrong in get_approved_posts, {e}')
    
    
@api_view(['PATCH'])
@csrf_exempt
@jwt_required
@parser_classes([MultiPartParser, FormParser])
def fix_post_issues(request):
    '''Update post is needed when there is a problem with the input of the user like rent docs, address and etc'''
    try:
        post_id = request.data.get('post_id')
        
        # extract the post needs to be updated
        post_to_update = Post.objects.get(post_id=post_id)

        # confirm_status is already changed in the dashboard admin by us when 'change_confirm_status()' is executed
        confirm_status = request.data.get('confirmation_status')
        
        err, post_to_update = activate_function_based_on_status(confirm_status, post_to_update, request.data)
        if err:
            return error_response(err)
                
        with transaction.atomic():
            post_to_update.confirmation_status = '0'  # needs to be approved again by the admin
            post_to_update.save()
            return success_response('Update post successfully')

    except Post.DoesNotExist:
        return error_response(f"Post with {post_id} not found")

    except Exception as e:
        return error_response(f"An error occurred during fix_post_details_after_posting function, {e}")


@api_view(['PATCH'])
@csrf_exempt
@jwt_required
@parser_classes([MultiPartParser, FormParser])
def update_apartment_pics(request):
    '''When a user upload a post and want to updated, add pic this endpoint will activate'''
    try:
        post_data = request.data

        post_id = post_data.get('post_id')
        post_to_update = Post.objects.get(post_id=post_id)

        post_to_update = PostSerializer(instance=post_to_update, data=request.data, partial=True)

        with transaction.atomic():
            if post_to_update.is_valid():
                post_to_update.save()
        
        return success_response('update_apartment_pics end successfully')

    except Post.DoesNotExist:
        return error_response('Post does not exist')
    
    except Exception as e:
        return error_response(f'Something is wrong in the update_apartment_pics, {e}')


@api_view(["PUT"])
@csrf_exempt
def update_confirm_status_field(request):
    '''This function is call by the admin dashboard, when a user upload a Post
    We check it and update the confirmation status accordingly'''

    try:
        
        confirmation_status = request.data.get('confirmation_status')
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')

        # update in 'Post' db the confirm status var
        update_confirm_status_in_post(post_id, confirmation_status)

        # extract the needed value of user_name for the message
        user_name = Users.objects.get(user_id=user_id).user_full_name

        # extract the right message according to the confirm_status value
        message, headline = extract_message_based_on_confirm_status(user_name, confirmation_status)

        # Add a message to the 'UserInbox' user db 
        UserInbox.objects.create(user_id=user_id,post_id=post_id,user_message=message,headline=headline)
        
        return success_response('Update confirmation status and create a new message in the user inbox successfully')

    except Exception as e:
        return error_response(f"An error occurred during update_confirm_status, {e}")
