from django.contrib.auth.backends import BaseBackend
from Users.models import Users  # Adjust this import according to your project's structure

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Users.objects.get(user_email=username)
            if user.check_password(password):
                return user
        except Users.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return None