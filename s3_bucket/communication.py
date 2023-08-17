import logging
from botocore.exceptions import ClientError
import boto3
import base64
from io import BytesIO
from django.http import JsonResponse

def get_image_from_s3(bucket_name:str, path:str):

    global s3_client
    s3_client = boto3.client('s3')

    try:
        buffer = BytesIO() 
        s3_client.download_fileobj(bucket_name, path, buffer)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logging.info('image_base64 was successfully encoded')
        return JsonResponse({'image': image_base64})
    except ClientError as e:
        logging.error(e)
        return False


def upload_file_to_s3(file_name:str, bucket:str,path_inside_s3:str) -> bool:

    try:
        response = s3_client.upload_file(file_name, bucket, path_inside_s3)
    except ClientError as e:
        logging.info(f"upload_file_to_s3 error")
        logging.error(e)
        return False
    return True


