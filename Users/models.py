from django.db import models


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)  # create primary key
    user_full_name = models.CharField(max_length=30)
    user_password = models.CharField(max_length=20)
    user_password_2 = models.CharField(max_length=20,default='None')
    user_email = models.CharField(max_length=50)
    user_phone = models.CharField(max_length=20)
