from rest_framework import serializers
from .models import UserInbox

class UserInboxSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = UserInbox
        fields = '__all__'  # This will serialize all fields in the UserInbox model