from rest_framework import serializers
from Users.models import Users


# This file helps us to convert the data complex data types to native python data types

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
