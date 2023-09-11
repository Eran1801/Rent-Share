import time
import os
import uuid
from django.db import models
from Users.models import Users

def generate_unique_filename(instance, filename):
    _, ext = os.path.splitext(filename)
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}_{ext}"
    return os.path.join('Posts', str(instance.post_user_id), str(instance.post_id), filename[:filename.index('.')] , unique_filename)

class ApartmentImage(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='apartment_images_related')
    image = models.ImageField(upload_to=generate_unique_filename)

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='posts') 
    post_city = models.CharField(max_length=50, null=False, blank=False)
    post_street = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_number = models.CharField(max_length=50, null=False, blank=False)
    post_apartment_price = models.CharField(max_length=10, null=False, blank=False)
    post_rent_start = models.DateField(null=False, blank=False)
    post_rent_end = models.DateField(null=False, blank=False) 

    proof_image = models.ImageField(upload_to=generate_unique_filename,null=False,blank=False)
    driving_license = models.ImageField(upload_to=generate_unique_filename,null=False,blank=False)

    apartment_images = models.ManyToManyField(ApartmentImage, related_name='posts')

    post_description = models.CharField(max_length=2000)
    proof_image_confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.post_id:
            last_post = Post.objects.last()
            if last_post:
                self.post_id = last_post.post_id + 1
            else:
                self.post_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.post_id)
