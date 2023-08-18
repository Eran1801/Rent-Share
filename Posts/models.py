import time
from django.db import models
from Users.models import Users
import os
import uuid
from django.db import models
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')  # Initialize the S3 client

def generate_unique_filename(instance, filename):
    _, ext = os.path.splitext(filename)
    
    # Generate a unique filename using a combination of UUID, timestamp, and original filename
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}_{ext}"
    
    # Check if the generated filename already exists in the S3 bucket
    while True:
        try:
            s3.head_object(Bucket='rent-buzz', Key=unique_filename)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Object not found, break the loop
                break
            else:
                # Handle other errors if needed
                raise
        unique_filename = f"{uuid.uuid4()}_{int(time.time())}_{ext}"
    
    return os.path.join('Post', str(instance.post_user_id), unique_filename)

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)  # create primary key

    #  relation with Users table, this means each post is associated with a user from the Users model.
    #  if user delete his account, all of it's post removes also.
    post_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='posts') #

    post_city = models.CharField(max_length=50)
    post_street = models.CharField(max_length=50)
    post_apartment_number = models.CharField(max_length=50)
    post_apartment_price = models.CharField(max_length=10)

    post_rent_start = models.DateField()
    post_rent_end = models.DateField()

    # Files to confirm that the user rent the house
    proof_image = models.ImageField(upload_to=generate_unique_filename,null=False)
    driving_license = models.ImageField(upload_to=generate_unique_filename,null=False)

    post_description = models.CharField(max_length=2000)

    proof_image_confirmed = models.BooleanField(default=False) # after confirm from admin turn to True

    apartment_pic_1 = models.ImageField(upload_to=generate_unique_filename,blank=True, null=True)
    # apartment_pic_2 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_3 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_4 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    