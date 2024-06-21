from django.urls import re_path

from Users.ForgotPasswordFlow.views_forgot_pass import forget_password, verify_code, reset_password
from Users.UserAuth.views_auth import register, login, delete_user
from Users.UserPersonalInfo.views_personal_info import change_password, change_personal_info, change_profile_picture, get_user_details

urlpatterns = [

    # authentication
    re_path(r'^register/$', register, name='register'),
    re_path(r'^login/$', login, name='login'),
    re_path(r'^delete_user/$', delete_user, name='delete_user'),

    # forgot-password flow
    re_path(r'^forget_password/$', forget_password, name='forget_password'),
    re_path(r'verify_password_reset_code/$', verify_code, name='verify_password_reset_code'),
    re_path(r'^reset_password/$', reset_password, name='reset_password'),

    # user profile
    re_path(r'^change_personal_info/$', change_personal_info, name='change_personal_info'),
    re_path(r'^change_password/$', change_password, name='change_password'),
    re_path(r'^change_profile_pic/$', change_profile_picture, name='change_profile_pic'),
    re_path(r'^get_user_details/$', get_user_details, name='get_user_details'),
]
