import logging
import base64
from django.core.files.base import ContentFile
import json

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
                # because if we have the same address we can post more then one on apartment
                grouped_apartments[location_key] = []
            
            # if the key exist we append the apartment to the list
            grouped_apartments[location_key].append(apartment_data)

        return grouped_apartments
    
    except Exception as e:
        logger.error(f"group_apartments_by_location: {e}")
        return {}


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
        return None


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
        post_data_dict['post_comments'] = post_data.get('post_comments')

        logger.info(f'post_data_dict: {post_data_dict}')
        return post_data_dict
    
    except Exception as e:
        logger.error(f"extract_post_data: {e}")
        return {}
    

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
        return {}
    

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
        return {}