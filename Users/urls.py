from django.urls import re_path

from Users import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^register/$', views.register, name='register'), 
    re_path(r'^login/$', views.login, name='login'),
]
