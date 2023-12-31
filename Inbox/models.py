from django.db import models

class UserInbox(models.Model):
    message_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50,null=False,blank=False)
    post_id = models.CharField(max_length=50, null=False, blank=False)
    user_message = models.CharField(max_length=200, default="")
    date = models.DateTimeField(auto_now_add=True)
