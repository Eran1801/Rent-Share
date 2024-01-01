from django.db import models
from django.db.models import BigAutoField

from Users.models import Users

class UserInbox(models.Model):
    message_id = BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE,related_name = 'messages')
    post_id = models.CharField(max_length=50, null=False, blank=False)
    user_message = models.CharField(max_length=200, default="")
    date = models.DateTimeField(auto_now_add=True)
