from django.contrib.auth.backends import BaseBackend
from .models import Users

# Custom Backend for Email Authentication
class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Users.objects.get(user_email=username)
            if user.check_password(password):
                return user
        except Users.DoesNotExist:
            return None
