from rest_framework import serializers
from Posts.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_id','post_user_email','post_city','post_street',
                 'post_apartment_number','post_apartment_price',
                 'post_rent_start','post_rent_end',
                 'proof_image','driving_license','post_description','proof_image_confirmed',
                 'apartment_pic_1')
        # ,'apartment_pic_2','apartment_pic_3','apartment_pic_4'