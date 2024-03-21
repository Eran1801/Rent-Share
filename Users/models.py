from django.db import models
import time
import os
import uuid
from typing import Any
from django.contrib.auth.hashers import check_password


def generate_unique_filename(instance: Any, filename: str):
    _, ext = os.path.splitext(filename)

    # Generate a unique filename using a combination of UUID, timestamp, and original filename
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}_{ext}"

    return os.path.join('Users', str(instance.user_id), filename[:filename.index('.')], unique_filename)


class Users(models.Model):

    user_id = models.AutoField(primary_key=True)  # create primary key
    user_full_name = models.CharField(max_length=25, blank=False, null=False)
    user_password = models.CharField(max_length=100, blank=False, null=False)
    user_email = models.EmailField(max_length=100, blank=False, null=False, unique=True)
    user_phone = models.CharField(max_length=10, blank=False, null=False, unique=True)
    user_profile_pic = models.ImageField(upload_to=generate_unique_filename, blank=True, null=True)

    def __str__(self):
        return f"User Id ({self.user_id})"
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.user_password)


class PasswordResetCode(models.Model):
    id = models.AutoField(primary_key=True)
    verification_code = models.CharField(max_length=5, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
