from django.db import models
from Users.models import Users

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)  # create primary key

    #  relation with Users table, this means each post is associated with a user from the Users model.
    post_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='posts') #

    post_city = models.CharField(max_length=50)
    post_street = models.CharField(max_length=50)
    post_apartment_number = models.CharField(max_length=50)
    post_apartment_price = models.CharField(max_length=10)

    post_rent_start = models.DateField()
    post_rent_end = models.DateField()

    # Files to confirm that the user rent the house
    proof_image = models.ImageField(upload_to='posts/images/',null=False)
    driving_license = models.ImageField(upload_to='posts/images',null=False)

    post_description = models.CharField(max_length=2000)

    proof_image_confirmed = models.BooleanField(default=False) # after confirm from admin turn to True

    apartment_pic_1 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_2 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_3 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    # apartment_pic_4 = models.ImageField(upload_to='posts/images',blank=True, null=True)
    