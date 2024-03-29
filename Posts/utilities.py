from datetime import datetime
import logging
import base64
from django.core.files.base import ContentFile
import json

from django.http import JsonResponse

'''
In this file there is all the helper function
for the Posts app and maybe others'''

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
        return []


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
                # because if we have the same address we can review more then one on apartment
                grouped_apartments[location_key] = []
            else:
                grouped_apartments[location_key].append(apartment_data)

        return grouped_apartments

    except Exception as e:
        logger.error(f"group_apartments_by_location: {e}")
        return {}


def convert_to_json(grouped_apartments):
    json_result = []

    for apartment_list in grouped_apartments.values():
        json_result.append(apartment_list)
    
    return json.dumps(json_result, ensure_ascii=False)


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
        return None


def extract_post_data(post_data: dict) -> dict:
    try:
        post = {}

        user = post_data.get('user')
        post['post_user_id'] = user.get('user_id')
        post['post_city'] = post_data.get('post_city')
        post['post_street'] = post_data.get('post_street')
        post['post_building_number'] = post_data.get('post_building_number')
        post['post_apartment_number'] = post_data.get('post_apartment_number')
        post['post_apartment_price'] = post_data.get('post_apartment_price')
        post['post_rent_start'] = post_data.get('post_rent_start')
        post['post_rent_end'] = post_data.get('post_rent_end')
        post['post_description'] = post_data.get('post_description')
        post['confirmation_status'] = '0'
        post['post_rating'] = post_data.get('post_rating')
        post['post_comments'] = post_data.get('post_comments')
        
        post = convert_images_to_files(post_data,post)

        logger.info(f'post: {post}')
        return post

    except Exception as e:
        logger.error(f"extract_post_data: {e}")
        return {}


def convert_images_to_files(post_data: dict, post:dict) -> dict:
    number_of_pics = 4

    try:
        rented_agreement_base64 = post_data.get('rent_agreement')
        logger.info(f'rent_agg = {rented_agreement_base64}')
        if rented_agreement_base64 is None:
            raise ValueError("A rented agreement is required")
        post['rent_agreement'] = convert_base64(rented_agreement_base64, "rent_agreement")

        driving_license_base64 = post_data.get('driving_license')
        if driving_license_base64 is None:
            raise ValueError("A driving license is required")
        post['driving_license'] = convert_base64(driving_license_base64, "driving_license")

        apartment_pics_base64 = []
        for i in range(number_of_pics):
            apartment_pics_base64.append(post_data.get(f'apartment_pic_{i + 1}'))

        for i, pic in enumerate(apartment_pics_base64):
            if pic is not None:
                post[f'apartment_pic_{i + 1}'] = convert_base64(pic, f"apartment_pic_{i + 1}")

        return post

    except Exception as e:
        logger.error(f"convert_images_to_files: {e}")
        return {}


def filter_cond(city, street, building, apr_number):
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
        return {}

def extract_fields_for_post_parm(post):
    city = post.GET.get('post_city') 
    street = post.GET.get('post_street',"")
    building_number = post.GET.get('post_building_number',"")
    apartment_number = post.GET.get('post_apartment_number',"")
        
    return city, street, building_number, apartment_number

def validate_post_parameters(city, street, building_number, apartment_number):
    """Validate the parameters for getting posts"""

    # Check if any of the required fields are missing or empty
    if city == '' or street == 'null' or apartment_number == 'null' or building_number == 'null': 
        return "At least one field is required"
    
    # Check if the city field is empty
    if city == '':
        return "City field is required"

    # If everything is fine, return None
    return None

            
def update_post_address(post, data):

    try:
        post.post_city = data.get('post_city')
        post.post_street = data.get('post_street')
        post.post_building_number = data.get('post_building_number')
        post.post_apartment_number = data.get('post_apartment_number')
    
    except Exception as e:
        logger.error(f"update_post_address: {e}")
        return JsonResponse({'message': 'Failed to update the address'}, status=400)
    
        
def update_post_rent_dates(post_to_update, post_data):
    
    try:
        new_rent_start_date = post_data.get('post_rent_start')
        new_rent_end_date = post_data.get('post_rent_end')

        new_rent_start_date = datetime.strptime(new_rent_start_date, '%Y-%m-%d').date()
        new_rent_end_date = datetime.strptime(new_rent_end_date, '%Y-%m-%d').date()

        post_to_update.post_rent_start = new_rent_start_date
        post_to_update.post_rent_end = new_rent_end_date
    except Exception as e:
        logger.error(f"update_post_rent_dates: {e}")
        return JsonResponse({'message': 'Failed to update the rented dates'}, status=400)
    
    
    
def update_post_driving_license(post_to_update, post_data):
    try:
        driving_license_base64 = post_data.get('driving_license')
        new_driving_license = convert_base64(driving_license_base64, "new driving license")

        post_to_update.driving_license = new_driving_license
    except Exception as e:
        logger.error(f"update_post_driving_license: {e}")
        return JsonResponse({'message': 'Failed to update the driving license'}, status=400)
        
def update_post_rent_agreement(post_to_update, post_data):
    
    try:
        rent_agreement_base64 = post_data.get('rent_agreement')
        new_rent_agreement = convert_base64(rent_agreement_base64, "new rent agreement")
        post_to_update.rent_agreement = new_rent_agreement
    except Exception as e:
        logger.error(f"update_post_rent_agreement: {e}")
        return JsonResponse({'message': 'Failed to update the rented agreement'}, status=400)
    
