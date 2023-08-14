from django.db import models

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)  # create primary key
    post_user_email = models.CharField(max_length=50)

    post_city = models.CharField(max_length=50)
    post_street = models.CharField(max_length=50)
    post_apartment_number = models.CharField(max_length=50)
    post_apartment_price = models.IntegerField()

    post_rent_start = models.DateField()
    post_rent_end = models.DateField()

    # Files to confirm that the user rent the house
    arnona_image = models.ImageField(upload_to='posts/images/')
    electricity_image = models.ImageField(upload_to='posts/images/')
    water_image = models.ImageField(upload_to='posts/images/')
    internet_image = models.ImageField(upload_to='posts/images/')
    contract_pdf = models.FileField(upload_to = 'posts/pdf')

    driving_license = models.ImageField(upload_to='posts/images')

    apartment_pic_1 = models.ImageField(upload_to='posts/images',)
    apartment_pic_2 = models.ImageField(upload_to='posts/images')
    apartment_pic_3 = models.ImageField(upload_to='posts/images')
    apartment_pic_4 = models.ImageField(upload_to='posts/images')


    