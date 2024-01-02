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
import base64
from django.core.files.base import ContentFile
from Users.views import *
import json
from django.core.exceptions import ObjectDoesNotExist

# Define the logger at the module level
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def process_apartments(apartment_data) -> list:
    '''This function will be used to process the apartments data and hold each apartment in a list'''
    try:
        apartments_list = []

        logger.info(f'apartment_data: {apartment_data}')

        for apr in apartment_data:
            apartments_list.append(apr)

        return apartments_list
    
    except Exception as e:
        logger.error(f"process_apartments: {e}")
        return HttpResponseServerError('An error occurred while processing apartments')

def group_apartments_by_location(apartments_data):
    '''This function will be used to group the apartments by location based on city, address, building number, and apartment number'''

    try:
        grouped_apartments = {}

        logger.info(f'apartments_data: {apartments_data}')

        # Iterate over each apartment in the list and get only the relevant fields
        for apartment_data in apartments_data:
            location_key = (
                apartment_data['post_city'],
                apartment_data['post_street'],
                apartment_data['post_building_number'],
                apartment_data['post_apartment_number']
            )

            # If the location key is not in the dictionary, add it with an empty list as the value
            if location_key not in grouped_apartments:
                # create a new key in the dictionary only if it doesn't exist
                # because if we have the same address we can post more then one on apartment
                grouped_apartments[location_key] = []
            
            # if the key exist we append the apartment to the list
            grouped_apartments[location_key].append(apartment_data)

        return grouped_apartments
    
    except Exception as e:
        logger.error(f"group_apartments_by_location: {e}")
        return HttpResponseServerError('An error occurred while grouping apartments by location')

def convert_to_json(grouped_apartments):
    json_result = []

    for apartment_list in grouped_apartments.values():
        json_result.append(apartment_list)

    return json.dumps(json_result,ensure_ascii=False)

def convert_base64(base64_str, filename):
    '''
    Convert base64-encoded images to actual files.
    
    Args:
        base64_str (str): Base64-encoded image string.
        filename (str): Desired filename for the output image file.
        
    Returns:
        ContentFile: The converted image data as a Django ContentFile.
    '''
    try:

        # split the base64 string into format and image data parts
        format, image_str = base64_str.split(';base64,')
        logger.info(f'format = {format} , image_str = {image_str}')
        
        # extract the image file extension from the format part
        ext = format.split('/')[-1]
        
        # decode the base64-encoded image data
        image_data = base64.b64decode(image_str)
        
        # create the full image filename with extension
        image_filename = f"{filename}.{ext}"
        
        # create a ContentFile object containing the image data
        # ContentFile - a file-like object that takes just raw content, rather than an actual file.
        content_file = ContentFile(image_data, name=image_filename)
        
        # return the ContentFile object
        return content_file
    
    except Exception as e:
        logger.error(f"convert_base64_to_image: {e}")
        return HttpResponseServerError('An error occurred while converting base64 to image')

def extract_post_data(post_data:str) -> dict:

    try:
        post_data_dict = {}

        user = post_data.get('user')
        logger.info(f'user: {user}')
        post_data_dict['post_user_id'] = user.get('user_id')
        post_data_dict['post_city'] = post_data.get('post_city')
        post_data_dict['post_street'] = post_data.get('post_street')
        post_data_dict['post_building_number'] = post_data.get('post_building_number')
        post_data_dict['post_apartment_number'] = post_data.get('post_apartment_number')
        post_data_dict['post_apartment_price'] = post_data.get('post_apartment_price')
        post_data_dict['post_rent_start'] = post_data.get('post_rent_start')
        post_data_dict['post_rent_end'] = post_data.get('post_rent_end')
        post_data_dict['post_description'] = post_data.get('post_description')
        post_data_dict['confirmation_status'] = '0'
        post_data_dict['post_rating'] = post_data.get('post_rating')

        logger.info(f'post_data_dict: {post_data_dict}')
        return post_data_dict
    
    except Exception as e:
        logger.error(f"extract_post_data: {e}")
        return HttpResponseServerError('An error occurred while extracting post data')

def convert_images_to_files(post_data:dict) -> dict:
    number_of_pics = 4
    post_data_dict = extract_post_data(post_data)

    try:
        rented_agreement_base64 = post_data.get('rent_agreement')
        logger.info(f'rent_agg = {rented_agreement_base64}')
        if rented_agreement_base64 is None:
            raise ValueError("A rented agreement is required")
        post_data_dict['rent_agreement'] = convert_base64(rented_agreement_base64, "rent_agreement")

        driving_license_base64 = post_data.get('driving_license')
        if driving_license_base64 is None:
            raise ValueError("A driving license is required")
        post_data_dict['driving_license'] = convert_base64(driving_license_base64, "driving_license")

        apartment_pics_base64 = []
        for i in range(number_of_pics):
            apartment_pics_base64.append(post_data.get(f'apartment_pic_{i+1}'))

        for i, pic in enumerate(apartment_pics_base64):
            if pic is not None:
                post_data_dict[f'apartment_pic_{i+1}'] = convert_base64(pic, f"apartment_pic_{i+1}")

        return post_data_dict

    except Exception as e:
        logger.error(f"convert_images_to_files: {e}")
        return HttpResponseServerError('An error occurred while converting images to files')

def filter_cond(city,street,building,apr_number):
    '''This function will gather all the values for the query to the db for extract the right post'''
    try:
        # we add the confirmation_status to the filter conditions because we want to show only the posts that the admin approved
        filter_conditions = {'post_city': city, 'confirmation_status': '1'}

        if street != 'null' and street != '':
            filter_conditions['post_street'] = street
        
        if building != 'null' and building != '':
            filter_conditions['post_building_number'] = building
        
        if apr_number != 'null' and apr_number != '':
            filter_conditions['post_apartment_number'] = apr_number
            if filter_conditions.get('post_building_number') != None:
                filter_conditions['post_apartment_number'] = apr_number

        return filter_conditions
    
    except Exception as e:
        logger.error(f"filter_cond : {e}")
        return HttpResponseServerError("An error occurred during filter_cond")


@api_view(['POST'])
@csrf_exempt
def add_post(request):
    '''This function will be used to add a new post'''

    try:
        post_data = request.data    
        logger.info(f'post_data after request.data: {post_data}')

        # inside convert_images_to_files we extract the post data and convert the images to files
        post_data_dict = convert_images_to_files(post_data)
        logger.info(f'post_data_dict after convert_images_to_files: {post_data_dict}')

        post = PostSerializerAll(data=post_data_dict, partial=True)
        logger.info(f'post: {post}')

        if post.is_valid():

            saved_post = post.save()
            logger.info(f'saved_post: {saved_post} and his type is {type(saved_post)}')

            if isinstance(saved_post,Post):

                # create a new value in Inbox table for this user with the right message and post_id
                user_name = post_data.get('user').get('user_full_name')
                logger.info(f'user_name: {user_name}')

                message = confirmation_status_messages(user_name,'0') # 0 means not confirmed yet
                logger.info(f'message: {message}')

                user_id = post_data.get('user').get('user_id')
                UserInbox.objects.create(user_id=user_id,post_id=saved_post.post_id,user_message=message)

                # send email to the company email that a new post was added
                msg = f"New post was added to S3.\nUser : {post_data.get('user').get('user_id')}"
                subject = "New post"
                send_email(FROM_EMAIL, FROM_EMAIL, msg, subject)
                
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
    '''This function will be used to get all the posts in the db 'Pots' table'''
    try:
        all_posts = Post.objects.all()
        all_posts_serialize = PostSerializerAll(all_posts,many=True) # many -> many objects
        return JsonResponse(all_posts_serialize.data, safe=False)

    except Exception as e:
         logger.error(f"get_all_posts : {e}")
         return HttpResponseServerError("An error occurred during get_all_posts")


@api_view(['GET'])
@csrf_exempt
def get_post_by_parm(request):
    '''This function will be used to get all the posts in the db 'Pots' table'''
    try:
        
        post_city = request.GET.get('post_city') 
        post_street = request.GET.get('post_street')
        post_building_number = request.GET.get('post_building_number')
        post_apartment_number = request.GET.get('post_apartment_number')

        # edge cases to check first        
        if post_city == '' and post_street == 'null' and post_apartment_number == 'null' and post_building_number == 'null': 
            return HttpResponseBadRequest("At least one field is required")

        if post_city == '':
            return HttpResponseBadRequest("City field is required")
        
        filter_conditions = filter_cond(post_city,post_street,post_building_number,post_apartment_number)
        logger.info(f'filter_conditions: {filter_conditions}')
        post = Post.objects.filter(**filter_conditions)
        logger.info(f'post: {post}')

        if post.exists():
            try:
                post_serializer = PostSerializerAll(post, many=True)

                # process the apartments to send it as json to the frontend 
                apartments = process_apartments(post_serializer.data)
                logger.info(f'apartments: {apartments}')
                grouped_apartments = group_apartments_by_location(apartments) 
                logger.info(f'grouped_apartments: {grouped_apartments}')
                json_result = convert_to_json(grouped_apartments)
                logger.info(f'json_result: {json_result}')

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
    '''This function will be used to get a post by its ID'''
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

        posts = Post.objects.filter(post_user_id=user_id) # get the post using post_id
        post_serializer = PostSerializerAll(posts, many=True) # more than one post
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
            post.post_description = post_description
            post.confirmation_status = '0'
            post.save() # save the updated post to the db
            send_email(FROM_EMAIL,FROM_EMAIL,f"User : {post.post_user_id}\nPost : {post_id}\ndescription has changed","Post description changed") # email to myself to notice the change
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
        logger.info(f'post_to_update = {post_to_update}')
        # confirmation_status
        # confirm_status is already change in the dashboard admin by us. when changes 'change_confirm_status()' is executed
        confirm_status = post_data.get('confirmation_status')
        logger.info(f'confirm_status inside update_post in Posts = {confirm_status}')
        logger.info(f'confirm_status type = {type(confirm_status)}')

        if confirm_status == '2':
        
            logger.info('post_city_before - {post_to_update.post_city}')
            post_to_update.post_city = post_data.get('post_city')

            logger.info('post_street_before - {post_to_update.post_street}')
            post_to_update.post_street = post_data.get('post_street')

            logger.info('post_building_number_before - {post_to_update.post_building_number}')
            post_to_update.post_building_number = post_data.get('post_building_number')

            logger.info('post_apartment_number_before - {post_to_update.post_apartment_number}')
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
            new_rent_agreement = convert_base64(rent_agreement_base64, "rent agreement")

            post_to_update.rent_agreement = new_rent_agreement
        
        elif confirm_status == '5':

            driving_license_base64 = post_data.get('driving_license')
            new_driving_license = convert_base64(driving_license_base64, "driving license")

            post_to_update.driving_license = new_driving_license

        post_to_update.confirmation_status = '0'
        post_to_update.save()
        logger.info(f'post_city_after - {post_to_update.post_city}')
        logger.info(f'post_street_after - {post_to_update.post_street}')
        logger.info(f'post_building_number_after - {post_to_update.post_building_number}')
        logger.info(f'post_apartment_number_after - {post_to_update.post_apartment_number}')


        return JsonResponse('Success to update the post',safe=False)

    except Post.DoesNotExist:
        logger.error('Post not found')

    except Exception as e:
        logger.error(e)
        logger.error('Something wrong with the update_post function in Posts.views')


@api_view(['PUT'])
@csrf_exempt
def update_aprtemanet_pics(request):

    try:
        post_data = request.data
        post_id = post_data.get('post_id')

        post_to_update = Post.objects.get(post_id=post_id)

        logger.info(f'update_aprtemanet_pics - post_to_update = {post_to_update}')

        max_pics = 4
        for i in range(max_pics):
            pic_base64 = post_data.get(f'apartment_pic_{i+1}')
            if pic_base64 is not None:
                '''setattr is used for dynamically setting an attribute of an object,
                identified by a string name, to a specified value.'''
                setattr(post_to_update, f'apartment_pic_{i+1}', convert_base64(pic_base64, f"apartment_pic_{i+1}"))     
        
        post_to_update.save()
        return JsonResponse('update_aprtemanet_pics end successfully')

    except ObjectDoesNotExist as e:
        logger.error(f'post dont exists {e}')
        return HttpResponseBadRequest('Post dont exists')
    
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('something is wrong in the update_aprtemanet_pics')