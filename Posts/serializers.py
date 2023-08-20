from rest_framework import serializers
from Posts.models import Post

class PostSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'  # This will serialize all fields in the Post model