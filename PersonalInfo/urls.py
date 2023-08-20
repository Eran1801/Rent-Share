from django.urls import re_path

from PersonalInfo import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^change_personal_info/$', views.change_personal_info, name='change_personal_info'), 
]