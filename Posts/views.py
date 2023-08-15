from django.http.response import JsonResponse
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging
from Posts.serializers import PostSerializer,PostSerializerAll
from Users.models import Users
from django.http import HttpResponseServerError
from Posts.models import Post
import base64
import io
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

# Define the logger at the module level
logger = logging.getLogger(__name__)

def convert_base64_to_image(base64_str, filename):
    format, image_str = base64_str.split(';base64,') 
    ext = format.split('/')[-1] 

    data = ContentFile(base64.b64decode(image_str), name=filename + '.' + ext)
    return data


@csrf_exempt
def add_post(request):
    logging.basicConfig(level=logging.DEBUG)

    if request.method == 'POST':
        post_data = JSONParser().parse(request)

        # post_user_email = post_data.get('user_email')
        post_user_email = post_data.get('user', {}).get('user_email')

        # Fetch the Users object based on the email
        try:
            user = Users.objects.get(user_email=post_user_email)
        except Users.DoesNotExist:
            return HttpResponseServerError('User not found')
        
        logger.info("User found.")

        post_city = post_data.get('post_city')
        post_street = post_data.get('post_street')
        post_apartment_number = post_data.get('post_apartment_number')
        post_apartment_price = post_data.get('post_apartment_price')
        
        post_rent_start = post_data.get('post_rent_start') # extract day, month, year 
        post_rent_end = post_data.get('post_rent_end') # extract day, month, year 

        proof_image_base64 = post_data.get('proof_image')[0]  # Extract the first item from the list
        proof_image_file = convert_base64_to_image(proof_image_base64, "proof_image")

        driving_license_base64 = post_data.get('driving_license')[0]
        driving_license_file = convert_base64_to_image(driving_license_base64, "driving_license")

        apartment_pic_1_base64 = post_data.get('apartment_pic_1')[0]
        apartment_pic_1_file = convert_base64_to_image(apartment_pic_1_base64, "apartment_pic_1")


        # proof_image = post_data.get('proof_image') # bool
        # driving_license = post_data.get('driving_license')

        # apartment_pic_1 = post_data.get('apartment_pic_1')
        # apartment_pic_2 = post_data.get('apartment_pic_2')
        # apartment_pic_3 = post_data.get('apartment_pic_3')
        # apartment_pic_4 = post_data.get('apartment_pic_4')

        post_description = post_data.get('post_description')

        post_data_dict = {
            'post_user': user.user_id,
            'post_city': post_city,
            'post_street': post_street,
            'post_apartment_number': post_apartment_number,
            'post_apartment_price': post_apartment_price,
            'post_rent_start': post_rent_start,
            'post_rent_end': post_rent_end,
            'proof_image': proof_image_file,
            'driving_license': driving_license_file,
            'apartment_pic_1': apartment_pic_1_file,
            'post_description': post_description
        }

        logger.info("post_data_dict created!.")

        '''
            apartment_pic_2=apartment_pic_2,
            apartment_pic_3=apartment_pic_3,
            apartment_pic_4=apartment_pic_4,
        '''

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
    logger.info("all_posts success.")

    response_data_serializer = PostSerializerAll(all_posts,many = True)
    logger.info("serializer success.")
    return JsonResponse(response_data_serializer.data, safe=False)
