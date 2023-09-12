from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
from Posts.serializers import PostSerializerAll
from Users.models import Users
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from Posts.models import Post
import base64
from django.core.files.base import ContentFile
from Users.views import *

# Define the logger at the module level
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
        return None

@api_view(['POST'])
@csrf_exempt
def add_post(request):
    '''This function will be used to add a new post'''

    post_data = request.data

    #post_id = post_data.get('post_id')
    post_user_email = post_data.get('user', {}).get('user_email')

    #logger.info(f'post_id: {post_id}')
    logger.info(f'post_user_email: {post_user_email}')

    # Fetch the Users object based on the email
    try:
        user = Users.objects.get(user_email=post_user_email)
    except Users.DoesNotExist:
        return HttpResponseServerError('User not found')  

    post_city = post_data.get('post_city')
    post_street = post_data.get('post_street')
    post_apartment_number = post_data.get('post_apartment_number')
    post_apartment_price = post_data.get('post_apartment_price')
    
    post_rent_start = post_data.get('post_rent_start')
    post_rent_end = post_data.get('post_rent_end')

    post_description = post_data.get('post_description')

    logger.info(f'post_city: {post_city}')
    logger.info(f'post_street: {post_street}')
    logger.info(f'post_apartment_number: {post_apartment_number}')
    logger.info(f'post_apartment_price: {post_apartment_price}')
    logger.info(f'post_rent_start: {post_rent_start}')
    logger.info(f'post_rent_end: {post_rent_end}')
    logger.info(f'post_description: {post_description}')

    proof_image_base64 = post_data.get('proof_image')[0]  # Extract the first item from the list
    proof_image_file = convert_base64(proof_image_base64, "proof_image")

    driving_license_base64 = post_data.get('driving_license')[0]
    driving_license_file = convert_base64(driving_license_base64, "driving_license")

    apartment_pic_1_base64 = post_data.get('apartment_pic_1')[0]
    apartment_pic_1_file = convert_base64(apartment_pic_1_base64, "apartment_pic_1")

    apartment_pic_2_base64 = post_data.get('apartment_pic_2')[0]
    apartment_pic_2_file = convert_base64(apartment_pic_2_base64, "apartment_pic_2")

    apartment_pic_3_base64 = post_data.get('apartment_pic_3')[0]
    apartment_pic_3_file = convert_base64(apartment_pic_3_base64, "apartment_pic_3")

    apartment_pic_4_base64 = post_data.get('apartment_pic_4')[0]
    apartment_pic_4_file = convert_base64(apartment_pic_4_base64, "apartment_pic_4")

    # creating a dict to pass to the serializer as the post
    post_data_dict = {
        'post_user_id': user.user_id,
        'post_city': post_city,
        'post_street': post_street,
        'post_apartment_number': post_apartment_number,
        'post_apartment_price': post_apartment_price,
        'post_rent_start': post_rent_start,
        'post_rent_end': post_rent_end,
        'proof_image': proof_image_file,
        'driving_license': driving_license_file,
        'apartment_pic_1': apartment_pic_1_file,
        'apartment_pic_2': apartment_pic_2_file,
        'apartment_pic_3': apartment_pic_3_file,
        'apartment_pic_4': apartment_pic_4_file,
        'post_description': post_description,
    }

    logger.info(f'post_data_dict: {post_data_dict}')

    post = PostSerializerAll(data=post_data_dict)
    if post.is_valid():
        try:
            post.save()  # Attempt to save to the database
            logger.info("Saved to the database")
            msg = f"New post was added to S3.\nUser : {user.user_id}"
            subject = "New post"
            send_email(FROM_EMAIL,FROM_EMAIL,msg,subject)
            return JsonResponse("Post successfully saved in db", safe=False)
        except Exception as e:
            logger.error(f"add_post : {e}")
            return HttpResponseServerError("An error occurred while saving the post")
    else:
        logger.debug(post.errors)
        return HttpResponseServerError("Post validation failed")

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
        logger.info(f'post_city: {post_city} and his type is {type(post_city)}')

        post_street = request.GET.get('post_street')
        logger.info(f'post_street: {post_street} and his type is {type(post_street)}')

        post_apartment_number = request.GET.get('post_apartment_number')
        logger.info(f'post_apartment_number: {post_apartment_number} and his type is {type(post_apartment_number)}')
        
        if post_city == '' and post_street == 'null' and post_apartment_number == 'null': 
            return HttpResponseBadRequest("At least one field is required")

        if post_city == '':
            return HttpResponseBadRequest("City field is required")

        # Construct the queryset conditions based on available parameters
        filter_conditions = {'post_city': post_city, 'proof_image_confirmed': True} # post_city is definitely not null

        if post_street != 'null' and post_street != '': # needs to check this 2 conditions
            logger.info(f'filter_conditions 1: {filter_conditions}')
            filter_conditions['post_street'] = post_street
        if post_apartment_number != 'null' and post_apartment_number != '':
            logger.info(f'filter_conditions 2: {filter_conditions}')
            filter_conditions['post_apartment_number'] = post_apartment_number

        logger.info(f'filter_conditions final: {filter_conditions}')

        post_v1 = Post.objects.filter(**filter_conditions)
        logger.info(f'post_v1: {post_v1}')

        if post_v1.exists():
            try:
                logger.info('After post_v1.exists()')
                post_serializer = PostSerializerAll(post_v1, many=True)
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
    '''This function will be used to get a post by its ID'''
    try:
        post_id = request.GET.get('post_id')
        logger.info('post_id: ' + post_id)

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
        logger.info(f'User ID: {user_id}')

        posts = Post.objects.filter(post_user_id=user_id) # get the post using post_id
        post_serializer = PostSerializerAll(posts, many=True) # more than one post
        logger.info(f'Post serializer: {post_serializer}')

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
            post.proof_image_confirmed = False
            post.save() # save the updated post to the db
            send_email(FROM_EMAIL,FROM_EMAIL,f"User : {post.post_user_id}\nPost : {post_id}\ndescription has changed","Post description changed")
            return JsonResponse("Description info updated successfully", safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred, update_description_post: {e}")

@api_view(['DELETE'])
@csrf_exempt
def delete_post(request):
    '''This function will be used to delete a post'''
    try:
        # getting data from the frontend
        post_id = request.GET.get('post_id')
        # user_id = request.GET.get('user_id')

        # logging the data (for debugging purposes)
        logger.info(f'post_id: {post_id}')
        # logger.info(f'user_id: {user_id}') 

        post = Post.objects.get(post_id=post_id) # get the post using post_id
        post.delete() # delete the post

        return JsonResponse("Post successfully deleted", safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred, delete_post: {e}")
