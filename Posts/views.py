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
    '''This function will be used to convert base64-encoded images to actual files'''
    format, image_str = base64_str.split(';base64,') 
    ext = format.split('/')[-1] 

    data = ContentFile(base64.b64decode(image_str), name=filename + '.' + ext)
    return data

@api_view(['POST'])
@csrf_exempt
def add_post(request):
    '''This function will be used to add a new post'''

    '''
    # todo
    Image Handling:
    our code for converting base64-encoded images to actual files seems fine.
    Just ensure that you handle any possible exceptions that might occur during 
    this conversion, such as invalid image formats or base64 data.
    '''

    post_data = request

    post_user_email = post_data.get('user', {}).get('user_email')

    # Fetch the Users object based on the email
    try:
        user = Users.objects.get(user_email=post_user_email)
    except Users.DoesNotExist:
        return HttpResponseServerError('User not found')
    
    logger.info("User found.")

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

    # TODO: update the list in the loop accordantly. 
    # apartment_pic_2_instance = post_data_dict['apartment_pic_2']
    # apartment_pic_2_filename = apartment_pic_2_instance.name

    # apartment_pic_3_instance = post_data_dict['apartment_pic_3']
    # apartment_pic_3_filename = apartment_pic_3_instance.name

    # apartment_pic_4_instance = post_data_dict['apartment_pic_4']
    # apartment_pic_4_filename = apartment_pic_4_instance.name

    post_serializer = PostSerializerAll(post_data_dict)
    if post_serializer.is_valid():
        post_serializer.save() # save to db
        logger.info("save to db")
        return JsonResponse("Post Success",safe=False)
    else:
        logger.debug(post_serializer.errors)
        return HttpResponseServerError("Post Fails")
    
@api_view(['GET'])
@csrf_exempt
def get_posts(request):
    '''This function will be used to get all posts'''

    all_posts = Post.objects.all()
    logger.info(f"all_posts : {all_posts}")

    all_posts_serialize = PostSerializerAll(all_posts,many = True) # many -> many objects
    logger.info("get_posts : serializer success.")
    return JsonResponse(all_posts_serialize.data, safe=False)

@api_view(['GET'])
@csrf_exempt
def get_post_by_id(request):
    '''This function will be used to get a post by its ID'''

    try:
        post_id:int = request.data.get('post_id')
        logger.info(f"get_post_by_id : post_id = {post_id}")

        post = Post.objects.get(post_id=post_id) # get the post using post_id
        logger.info("get_post_by_id : post by user_id success.")

        post_serializer = PostSerializerAll(post)
        return JsonResponse(post_serializer.data, safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")

@api_view(['GET'])
@csrf_exempt
def get_post_by_user_id(request):
    '''This function will be used to get a post by its user ID'''

    try:
        user_id = request.data

        posts = Post.objects.get(post_user_id=user_id) # get the post using post_id
    
        if posts.count() == 1:
            post_serializer = PostSerializerAll(posts)
        else:
            post_serializer = PostSerializerAll(posts, many=True) # more than one post

        return JsonResponse(post_serializer.data, safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")
     

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
                    return HttpResponseServerError("Post not found")
                else:
                    return PostSerializerAll(post_v3).data
            else:
                return PostSerializerAll(post_v2).data
        else:
            return PostSerializerAll(post_v1).data
            
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")
    
@api_view(['PUT'])
@csrf_exempt
def update_description_post(request):
    '''This function will be used to update the description of a post'''

    try:
        post_data = request.data

        post_id = post_data.get('post_id')
        post_description = post_data.get('post_description')

        post = Post.objects.get(post_id=post_id) # get the post using post_id

        post.post_description = post_description
        post.save()

        post_serializer = PostSerializerAll(post)
        return JsonResponse(post_serializer.data, safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")