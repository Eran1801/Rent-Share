from datetime import datetime
import logging
import json
from Posts.models import Post
from django.db import transaction
from Posts.serializers import PostSerializer

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

            
def update_post_address(post_to_update, request):

    try:
        post_to_update.post_city = request.get('post_city')
        post_to_update.post_street = request.get('post_street')
        post_to_update.post_building_number = request.get('post_building_number')
        post_to_update.post_apartment_number = request.get('post_apartment_number')
    
    except Exception as e:
        return str(e)
    
        
def update_post_rent_dates(post_to_update, request):
    try:
        new_rent_start_date = request.get('post_rent_start')
        new_rent_end_date = request.get('post_rent_end')

        new_rent_start_date = datetime.strptime(new_rent_start_date, '%Y-%m-%d').date()
        new_rent_end_date = datetime.strptime(new_rent_end_date, '%Y-%m-%d').date()

        post_to_update.post_rent_start = new_rent_start_date
        post_to_update.post_rent_end = new_rent_end_date
    
    except Exception as e:
        return str(e)
    
    
def update_post_driving_license(post_to_update, request):
    try:
        with transaction.atomic():
            post_to_update.confirmation_status = '0'  # needs to be approved again by the admin
            post_to_update = PostSerializer(
                instance=post_to_update, 
                data=request, 
                partial=True
            )
            
            if post_to_update.is_valid():
                return None, post_to_update
            
    except Exception as e:
        return str(e)
        
        
def update_post_rent_agreement(post_to_update, request):
    try:
        with transaction.atomic():
            post_to_update.confirmation_status = '0'  # needs to be approved again by the admin
            post_to_update = PostSerializer(
                instance=post_to_update, 
                data=request, 
                partial=True
            )
            
            if post_to_update.is_valid():
                return None, post_to_update
            
    except Exception as e:
        return str(e)

def activate_function_based_on_status(status, post_to_update, post_data) -> Post:
    
    if status == '2':
        err = update_post_address(post_to_update, post_data)
        
    elif status == '3':
        err = update_post_rent_dates(post_to_update, post_data)
        
    elif status == '4':
        err, post_to_update = update_post_rent_agreement(post_to_update, post_data)

    elif status == '5':
        err, post_to_update = update_post_driving_license(post_to_update, post_data)

    return err, post_to_update