import time
from typing import Any
from django.db import models
from Users.models import Users
import os
import uuid
from django.db import models

def generate_unique_filename(instance:Any, filename:str):
    _, ext = os.path.splitext(filename)

    # Generate a unique filename using a combination of UUID, timestamp, and original filename
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}_{ext}"
    
    return os.path.join('Posts', str(instance.post_user_id), filename[:filename.index('.')] ,unique_filename)

class Post(models.Model):
    
    post_id = models.AutoField(primary_key=True)  # create primary key

    #  relation with Users table, this means each post is associated with a user from the Users model.
    #  if user delete his account, all of it's post removes also.
    post_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='posts') #

    post_city = models.CharField(max_length=50, null=False, blank=False)
    post_street = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_number = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_price = models.CharField(max_length=10, null=False, blank=False)

    post_rent_start = models.DateField(null=False, blank=False)
    post_rent_end = models.DateField(null=False, blank=False) 

    # Files to confirm that the user rent the house
    proof_image = models.ImageField(upload_to=generate_unique_filename(post_id),null=False,blank=False) # TODO: MAYBE WRONG HERE BECAUSE SENDIN
    driving_license = models.ImageField(upload_to=generate_unique_filename,null=False,blank=False)

    post_description = models.CharField(max_length=2000)

    proof_image_confirmed = models.BooleanField(default=False) # after confirm from admin turn to True

    apartment_pic_1 = models.ImageField(upload_to=generate_unique_filename,blank=True, null=True)
    # apartment_pic_2 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_3 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_4 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    