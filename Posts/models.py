from typing import Any
from django.db import models
import os
import uuid
from datetime import datetime

def generate_unique_filename(instance, file_name: str, folder_name):
    _, ext = os.path.splitext(file_name)
    formatted_time = datetime.now().strftime("%d-%m-%Y_%H-%M")
    unique_filename = f"{uuid.uuid4()}_{formatted_time}{ext}"
    return os.path.join('Posts', str(instance.post_user_id), str(instance.post_id), folder_name, unique_filename)

def upload_to_rent_docs(instance, filename):
    return generate_unique_filename(instance, filename, 'rent_docs')

def upload_to_apartment_pics(instance, filename):
    return generate_unique_filename(instance, filename, 'apartment_pics')

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_user_id = models.IntegerField(null=False, blank=False)
    
    post_city = models.CharField(max_length=50, null=False, blank=False)
    post_street = models.CharField(max_length=50, null=False, blank=False)
    post_building_number = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_number = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_price = models.CharField(max_length=10, null=False, blank=False)
    post_rent_start = models.DateField(null=False, blank=False)
    post_rent_end = models.DateField(null=False, blank=False)
    post_review = models.CharField(max_length=5000, null=False, blank=False)
    post_rating = models.CharField(max_length=3, null=False, blank=False, default='0')
    confirmation_status = models.CharField(max_length=2, null=False, blank=False, default='0')
    
    rent_agreement = models.FileField(upload_to=upload_to_rent_docs, null=False, blank=False)
    driving_license = models.FileField(upload_to=upload_to_rent_docs, null=False, blank=False)
    
    apartment_pic_1 = models.ImageField(upload_to=upload_to_apartment_pics, blank=True, null=True)
    apartment_pic_2 = models.ImageField(upload_to=upload_to_apartment_pics, blank=True, null=True)
    apartment_pic_3 = models.ImageField(upload_to=upload_to_apartment_pics, blank=True, null=True)
    apartment_pic_4 = models.ImageField(upload_to=upload_to_apartment_pics, blank=True, null=True)
    
    user_addition_comments = models.CharField(max_length=2000, null=True, blank=True, default='No comment')

    def __str__(self):
        return f'Post id ({self.post_id})'

    def save(self, *args, **kwargs):
        if not self.post_id:
            last_post = Post.objects.last()
            if last_post is not None:
                self.post_id = last_post.post_id + 1
            else:
                self.post_id = 1
        super().save(*args, **kwargs)
