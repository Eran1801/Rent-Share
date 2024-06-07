from rest_framework import serializers
from .models import UserInbox

class UserInboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInbox
        fields = '__all__'  # This will serialize all fields in the UserInbox model