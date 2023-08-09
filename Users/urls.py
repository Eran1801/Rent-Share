from django.urls import re_path

from Users import views

urlpatterns = [
    re_path(r'^register/$', views.users_api, name='register'),
    re_path(r'^register/(?P<user_id>\d+)/$', views.users_api, name='register'),
]
