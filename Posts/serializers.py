from rest_framework import serializers
from Posts.models import Post

class PostSerializer(serializers.ModelSerializer):
    proof_image = serializers.ImageField(max_length=None, use_url=False)
    driving_license = serializers.ImageField(max_length=None, use_url=False)
    apartment_pic_1 = serializers.ImageField(max_length=None, use_url=False)  # Handle optional image file

    class Meta:
        model = Post
        fields = ('post_id', 'post_user', 'post_city', 'post_street',
                  'post_apartment_number', 'post_apartment_price',
                  'post_rent_start', 'post_rent_end',
                  'proof_image', 'driving_license', 'post_description', 'proof_image_confirmed',
                  'apartment_pic_1')
        # ,'apartment_pic_2','apartment_pic_3','apartment_pic_4'
