from django.db.models import Q
from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
from Posts.serializers import PostSerializerAll
from Users.models import Users
from django.http import HttpResponseBadRequest, HttpResponseServerError
from Posts.models import Post
import base64
from django.core.files.base import ContentFile

# Define the logger at the module level
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def convert_base64_to_image(base64_str, filename):
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

    post_user_email = post_data.get('user', {}).get('user_email')

    # Fetch the Users object based on the email
    try:
        user = Users.objects.get(user_email=post_user_email)
    except Users.DoesNotExist:
        return HttpResponseServerError('User not found')    

    #! tell mor to handle the date error in the front end but also in the backend

    post_city = post_data.get('post_city')
    post_street = post_data.get('post_street')
    post_apartment_number = post_data.get('post_apartment_number')
    post_apartment_price = post_data.get('post_apartment_price')
    
    post_rent_start = post_data.get('post_rent_start')
    post_rent_end = post_data.get('post_rent_end')

    post_description = post_data.get('post_description')

    proof_image_base64 = post_data.get('proof_image')[0]  # Extract the first item from the list
    proof_image_file = convert_base64_to_image(proof_image_base64, "proof_image")

    driving_license_base64 = post_data.get('driving_license')[0]
    driving_license_file = convert_base64_to_image(driving_license_base64, "driving_license")

    apartment_pic_1_base64 = post_data.get('apartment_pic_1')[0]
    apartment_pic_1_file = convert_base64_to_image(apartment_pic_1_base64, "apartment_pic_1")

    # apartment_pic_2_base64 = post_data.get('apartment_pic_2')[0]
    # apartment_pic_2_file = convert_base64_to_image(apartment_pic_2_base64, "apartment_pic_2")

    # apartment_pic_3_base64 = post_data.get('apartment_pic_3')[0]
    # apartment_pic_3_file = convert_base64_to_image(apartment_pic_3_base64, "apartment_pic_3")

    # apartment_pic_4_base64 = post_data.get('apartment_pic_4')[0]
    # apartment_pic_4_file = convert_base64_to_image(apartment_pic_4_base64, "apartment_pic_4")

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
        'post_description': post_description,
    }

    # ADD this to the dict 
    """
    # todo : add the rest of the images int the above dict
    'apartment_pic_2' : apartment_pic_2_file,
    'apartment_pic_3' : apartment_pic_3_file,
    'apartment_pic_4' : apartment_pic_4_file,
    """

    # apartment_pic_2_instance = post_data_dict['apartment_pic_2']
    # apartment_pic_2_filename = apartment_pic_2_instance.name

    # apartment_pic_3_instance = post_data_dict['apartment_pic_3']
    # apartment_pic_3_filename = apartment_pic_3_instance.name

    # apartment_pic_4_instance = post_data_dict['apartment_pic_4']
    # apartment_pic_4_filename = apartment_pic_4_instance.name

    post_serializer = PostSerializerAll(data=post_data_dict)
    if post_serializer.is_valid():
        try:
            post_serializer.save()  # Attempt to save to the database
            logger.info("Saved to the database")
            return JsonResponse("Post successfully saved in db", safe=False)
        except Exception as e:
            logger.error(f"add_post : {e}")
            return HttpResponseServerError("An error occurred while saving the post")
    else:
        logger.debug(post_serializer.errors)
        return HttpResponseServerError("Post validation failed")

@api_view(['GET'])
@csrf_exempt
def get_posts(request):
    '''This function will be used to get all the posts in the db 'Pots' table'''

    try:
        all_posts = Post.objects.all()

        all_posts_serialize = PostSerializerAll(all_posts,many=True) # many -> many objects
        if all_posts_serialize.is_valid():
            logger.info("Successfully serialized all the posts")
            return JsonResponse(all_posts_serialize.data, safe=False)
        else:
             logger.debug(all_posts_serialize.errors)
             return HttpResponseServerError("An error occurred while serialize all the posts")
    except Exception as e:
         logger.error(f"get_posts : {e}")
         return HttpResponseServerError("An error occurred get_posts")

@api_view(['GET'])
@csrf_exempt
def get_post_by_id(request):
    '''This function will be used to get a post by its ID'''

    try:
        post_id:int = request.data.get('post_id')
        logger.info('post_id: ' + str(post_id))

        post = Post.objects.get(post_id=post_id) # get the post using post_id

        post_serializer = PostSerializerAll(data=post)
        if post_serializer.is_valid():
            logger.info("Successfully serialized the post")
            return JsonResponse(post_serializer.data, safe=False)
        else:
            logger.debug(post_serializer.errors)
            return HttpResponseServerError("An error occurred while serialize the post")

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred get_post_by_id: {e}")

@api_view(['GET'])
@csrf_exempt
def get_post_by_user_id(request):
    '''This function will be used to get a post by its user ID'''
    try:
        user_id = request.data

        posts = Post.objects.get(post_user_id=user_id) # get the post using post_id
        post_serializer = None
    
        if posts.count() == 1:
            post_serializer = PostSerializerAll(data=posts)
        else:
            post_serializer = PostSerializerAll(data=posts, many=True) # more than one post

        if post_serializer.is_valid():
            logger.info("Successfully serialized the post")
            return JsonResponse(post_serializer.data, safe=False)
        else:
            logger.debug(post_serializer.errors)
            return HttpResponseServerError("An error occurred while serialize the post")
        
    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")

def serialize_post(post:Post):
    post_serializer = PostSerializerAll(data=post)
    if post_serializer.is_valid():
        logger.info("Successfully serialized the post")
        return JsonResponse(post_serializer.data, safe=False)
    else:
        logger.debug(post_serializer.errors)
        return HttpResponseServerError("An error occurred while serialize the post in get_post_by_city_street_apartment")

@api_view(['GET'])
@csrf_exempt
def get_post_by_city_street_apartment(request):
    '''
    This function will be used to get a post by its city, street, and apartment number.
    If the apartment number is not provided, the function will return all posts that match the city and street.
    If the street is not provided, the function will return all posts that match the city.
    '''

    try:
        post_data = request.data

        post_city = post_data.get('post_city')
        post_street = post_data.get('post_street')
        post_apartment_number = post_data.get('post_apartment_number')

        if len(post_city) == 0  and len(post_street) and len(post_apartment_number) == 0:
            return HttpResponseBadRequest("All fields are empty")
        if len(post_city) == 0:
            return HttpResponseBadRequest("City field is required")

        post_v1 = Post.objects.filter(post_city=post_city, post_street=post_street,post_apartment_number=post_apartment_number)
        post_v2 = Post.objects.filter(post_city=post_city, post_street=post_street)
        post_v3 = Post.objects.filter(post_city=post_city)

        if not post_v1 :
            if not post_v2:
                if not post_v3 == 0:
                    return HttpResponseServerError("Post not found") # all fields are missing   
                else:
                    serialize_post(post_v3) # only city is provided
            else:
                return serialize_post(post_v2)# city and street are provided
        else:
            return serialize_post(post_v3) # all fields are provided
            
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred, get_post_by_city.. : {e}")
    
@api_view(['PUT'])
@csrf_exempt
def update_description_post(request):
    '''This function will be used to update the description of a post'''

    post_data = request.data

    post_id = post_data.get('post_id')
    post_description = post_data.get('post_description')

    try:
        post = Post.objects.get(post_id=post_id) # get the post using post_id
        post.post_description = post_description # update the description

        post_serializer = PostSerializerAll(data=post)
        if post_serializer.is_valid():
            logger.info("Successfully serialized the post after update the description")
            post.save() # save the updated post to the db
            return JsonResponse(post_serializer.data, safe=False)  # return the updated post to frontend
        else:
            logger.debug(post_serializer.errors)
            return HttpResponseServerError("An error occurred while serialize the post after update the description")

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred, update_description_post: {e}")