from django.urls import re_path

from Inbox import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^update_confirm_status/$', views.update_confirm_status, name='update_confirm_status'), 
    
]