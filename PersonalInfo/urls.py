from django.urls import re_path

from PersonalInfo import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^change_personal_info/$', views.change_personal_info, name='change_personal_info'), 
    re_path(r'^change_password/$', views.change_password, name='change_password'),
    re_path(r'^change_profile_pic/$', views.change_profile_picture, name='change_profile_pic'),
    re_path(r'^get_profile_pic/$', views.get_profile_pic, name='get_profile_pic'),
    
]