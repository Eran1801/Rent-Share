from django.shortcuts import render
from django.views.decorators.csrf import \
    csrf_exempt  # will be used to exempt the CSRF token (Angular will handle CSRF token)
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@api_view(['PUT'])
@csrf_exempt
def change_personal_info(request):
    user_data = JSONParser().parse(request)

    #  find the user inside the db based on the email and then update the fields
    
    logger.info(f'user_data = {user_data}')