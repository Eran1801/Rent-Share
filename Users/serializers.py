from rest_framework import serializers
from Users.models import Users


# This file helps us to convert the data complex data types to native python data types

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_id', 'user_full_name', 'user_password', 'user_email', 'user_phone')
