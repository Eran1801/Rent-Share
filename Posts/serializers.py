from rest_framework import serializers
from Posts.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_id','post_user_email','post_city','post_street',
                 'post_apartment_number','post_apartment_price',
                 'post_rent_start','post_rent_end',
                 'arnona_image','electricity_image','water_image',
                 'internet_image','contract_pdf','driving_license',
                 'apartment_pic_1','apartment_pic_2','apartment_pic_3','apartment_pic_4')

