from django.urls import re_path

from Users import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^register/$', views.register, name='register'), 
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^delete_user/$', views.delete_user, name='delete_user'),
    re_path(r'^forget_password/$', views.forget_password, name='forget_password'),
    re_path(r'^reset_password/$', views.reset_password, name='reset_password'),
]
