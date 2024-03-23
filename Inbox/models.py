from django.db import models
from django.db.models import BigAutoField
from datetime import datetime

from Users.models import Users

class UserInbox(models.Model):
    message_id = BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE,related_name = 'messages') # creates a database column that stores the primary key of the related model.
    post_id = models.CharField(max_length=50, null=False, blank=False)
    user_message = models.CharField(max_length=200, default="")
    date = models.DateTimeField(auto_now_add=True)
    read_status = models.CharField(max_length=10,default="0") # 0 means message don't read
    headline = models.CharField(max_length=1000,default='') # the headline of the message