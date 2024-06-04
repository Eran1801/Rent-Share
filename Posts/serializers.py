from rest_framework import serializers
from .models import Post

class PostSerializerAll(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            'post_id',
            'post_city',
            'post_street',
            'post_building_number',
            'post_apartment_number',
            'post_apartment_price',
            'post_rent_start',
            'post_rent_end',
            'post_review',
            'post_rating',
            'confirmation_status',
            'rent_agreement',
            'driving_license',
            'apartment_pic_1',
            'apartment_pic_2',
            'apartment_pic_3',
            'apartment_pic_4',
            'user_addition_comments'
        )


class PostSerializerRentAgreement(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('rent_agreement',)
        
        

class PostSerializerDrivingLicense(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('driving_license',)
        