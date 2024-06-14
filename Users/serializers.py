from rest_framework import serializers
from Users.models import Users, PasswordResetCode


# This file helps us to convert the data complex data-types to native python data types

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_id', 'user_full_name', 'user_password', 'user_email', 'user_phone')
        
class UserSerializerPicture(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_profile_pic',)  


class UserSerializerProfileDetails(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_profile_pic', 'user_full_name', 'user_email', 'user_phone')


# Password Reset Code Model
class PasswordResetCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetCode
        fields = "__all__"
