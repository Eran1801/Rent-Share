import time
from typing import Any
from django.db import models
from Users.models import Users
import os
import uuid
from django.db import models
from datetime import datetime
from dirtyfields import DirtyFieldsMixin


def generate_unique_filename(instance, filename: str):
    _, ext = os.path.splitext(filename)
    # unique_filename = f"{uuid.uuid4()}_{int(time.time())}_{ext}"

    # Format the current time to include only date, hour, and minute
    formatted_time = datetime.now().strftime("%Y%m%d_%H%M")

    # Create the unique filename    
    ext = "ext" 
    unique_filename = f"{uuid.uuid4()}_{formatted_time}_{ext}"
    return os.path.join('Posts', str(f'User id = {instance.post_user_id}'), str(f'Post id = {instance.post_id}'), filename[:filename.index('.')] , unique_filename)

class Post(DirtyFieldsMixin,models.Model):
    
    post_id = models.AutoField(primary_key=True)  # create primary key

    #  relation with Users table, this means each post is associated with a user from the Users model.
    #  if user delete his account, all of it's post removes also.
    post_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='posts') 

    post_city = models.CharField(max_length=50, null=False, blank=False)
    post_street = models.CharField(max_length=50, null=False, blank=False)
    post_building_number = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_number = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_price = models.CharField(max_length=10, null=False, blank=False)

    post_rent_start = models.DateField(null=False, blank=False)
    post_rent_end = models.DateField(null=False, blank=False)

    post_description = models.CharField(max_length=2000,null=False, blank=False)
    post_rating = models.CharField(max_length=3,null=False, blank=False, default='0')

    confirmation_status = models.CharField(max_length=1,null=False,blank=False,default='0') # after confirm from admin turn to True

    # Files to confirm that the user rent the house
    rent_agreement = models.FileField(upload_to=generate_unique_filename,null=False,blank=False)
    driving_license = models.FileField(upload_to=generate_unique_filename,null=False,blank=False)

    apartment_pic_1 = models.ImageField(upload_to=generate_unique_filename,blank=True, null=True)
    apartment_pic_2 = models.ImageField(upload_to=generate_unique_filename,blank=True, null=True)
    apartment_pic_3 = models.ImageField(upload_to=generate_unique_filename,blank=True, null=True)
    apartment_pic_4 = models.ImageField(upload_to=generate_unique_filename,blank=True, null=True)

    post_comments = models.CharField(max_length=2000, null=True, blank=True,default='No comment')

    # override the save method to customize post_id behavior.
    def save(self, *args, **kwargs):
        # check if post_id is not set (it's a new post).
        if not self.post_id:
            # query the database for the last post.
            last_post = Post.objects.last()
            # If there is a last post, increment its post_id.
            if last_post is not None:
                self.post_id = last_post.post_id + 1
            else:
                # If there are no existing posts, set post_id to 1.
                self.post_id = 1
        # Call the original save method to save the model instance to the database.
        super().save(*args, **kwargs)
