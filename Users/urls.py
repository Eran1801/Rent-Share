from django.urls import re_path

from Users import views
from Users.auth import views_auth
from Users.personal_info import views_personal_info


urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^register/$', views_auth.register, name='register'),
    re_path(r'^login/$', views_auth.login, name='login'),
    re_path(r'^delete_user/$', views_auth.delete_user, name='delete_user'),

    re_path(r'^forget_password/$', views.forget_password, name='forget_password'),
    re_path(r'verify_password_reset_code/$', views.verify_code, name='verify_password_reset_code'),
    re_path(r'^reset_password/$', views.reset_password, name='reset_password'),

    re_path(r'^change_personal_info/$', views_personal_info.change_personal_info, name='change_personal_info'),
    re_path(r'^change_password/$', views_personal_info.change_password, name='change_password'),
    re_path(r'^change_profile_pic/$', views_personal_info.change_profile_picture, name='change_profile_pic'),
    re_path(r'^get_profile_pic/$', views_personal_info.get_profile_pic, name='get_profile_pic'),
]
