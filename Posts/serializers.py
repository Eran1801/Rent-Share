from rest_framework import serializers
from Posts.models import Post, ApartmentImage

class ApartmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentImage
        fields = '__all__'

class PostSerializerAll(serializers.ModelSerializer):
    apartment_images = ApartmentImageSerializer(many=True, read_only=True)  # Include related images

    class Meta:
        model = Post
        fields = '__all__'
