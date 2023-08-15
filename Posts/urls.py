from django.urls import re_path

from Posts import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^add_post/$', views.add_post, name='add_post'), 
    re_path(r'^feed_posts/$', views.get_posts, name='get_posts'), 
]