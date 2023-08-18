from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
from Posts.serializers import PostSerializer,PostSerializerAll
from Users.models import Users
from django.http import HttpResponseBadRequest, HttpResponseServerError
from Posts.models import Post
import base64
from django.core.files.base import ContentFile

# Define the logger at the module level
logger = logging.getLogger(__name__)

def convert_base64_to_image(base64_str, filename):
    format, image_str = base64_str.split(';base64,') 
    ext = format.split('/')[-1] 

    data = ContentFile(base64.b64decode(image_str), name=filename + '.' + ext)
    return data

@api_view(['POST'])
@csrf_exempt
def add_post(request):

    logging.basicConfig(level=logging.DEBUG)

    post_data = JSONParser().parse(request)

    post_user_email = post_data.get('user', {}).get('user_email')

    # Fetch the Users object based on the email
    try:
        user = Users.objects.get(user_email=post_user_email)
    except Users.DoesNotExist:
        return HttpResponseServerError('User not found')
    
    logger.info("User found.")

    #! tell mor to handle the date error in the front end but also in the frontend

    post_city = post_data.get('post_city')
    post_street = post_data.get('post_street')
    post_apartment_number = post_data.get('post_apartment_number')
    post_apartment_price = post_data.get('post_apartment_price')
    
    post_rent_start = post_data.get('post_rent_start') # extract day, month, year 
    post_rent_end = post_data.get('post_rent_end') # extract day, month, year 

    post_description = post_data.get('post_description')

    '''
    # todo
    Image Handling:
    our code for converting base64-encoded images to actual files seems fine.
    Just ensure that you handle any possible exceptions that might occur during 
    this conversion, such as invalid image formats or base64 data.
    '''

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

    '''
        # todo : add the rest of the images int the above dict
        'apartment_pic_2' : apartment_pic_2_file,
        'apartment_pic_3' : apartment_pic_3_file,
        'apartment_pic_4' : apartment_pic_4_file,
    '''

    # TODO: update the list in the loop accordantly. 
    # apartment_pic_2_instance = post_data_dict['apartment_pic_2']
    # apartment_pic_2_filename = apartment_pic_2_instance.name

    # apartment_pic_3_instance = post_data_dict['apartment_pic_3']
    # apartment_pic_3_filename = apartment_pic_3_instance.name

    # apartment_pic_4_instance = post_data_dict['apartment_pic_4']
    # apartment_pic_4_filename = apartment_pic_4_instance.name

    post_serializer = PostSerializer(data=post_data_dict)
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
    logging.basicConfig(level=logging.DEBUG)

    all_posts = Post.objects.all()
    logger.info("get_posts : all_posts success.")

    all_posts_serialize = PostSerializerAll(all_posts,many = True) # many -> many objects
    logger.info("get_posts : serializer success.")
    return JsonResponse(all_posts_serialize.data, safe=False)

@api_view(['POST'])
@csrf_exempt
def get_post_by_id(request):

    logging.basicConfig(level=logging.DEBUG)

    try:
        post_id:int = JSONParser().parse(request)
        logger.info(f"get_post_by_id : post_id = {post_id}")

        post = Post.objects.get(post_id=post_id) # get the post using post_id
        logger.info("get_post_by_id : post by user_id success.")

        post_serializer = PostSerializerAll(post)
        return JsonResponse(post_serializer.data, safe=False)

    except Post.DoesNotExist:
            return HttpResponseBadRequest("Post with the given ID does not exist.")
    except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {e}")
