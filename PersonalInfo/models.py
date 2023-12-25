from django.db import models

class Inbox(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True,null=False,blank=False)
    user_message_1 = models.CharField(max_length=200, default="")
    user_message_2 = models.CharField(max_length=200, default="")
    user_message_3 = models.CharField(max_length=200, default="")
    user_message_4 = models.CharField(max_length=200, default="")
    user_message_5 = models.CharField(max_length=200, default="")
    user_message_6 = models.CharField(max_length=200, default="")

