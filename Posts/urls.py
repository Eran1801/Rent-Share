from django.urls import re_path

from Posts import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^add_post/$', views.add_post, name='add_post'), 
    re_path(r'^feed_posts/$', views.get_posts, name='get_posts'),
    re_path(r'^get_post/$', views.get_post_by_id, name='get_post'), 
    re_path(r'^city_street_apartment/$', views.get_post_by_city_street_apartment, name='get_post_by_city_street_apartment'),
    re_path(r'^get_post_by_user_id/$', views.get_post_by_user_id, name='get_post_by_user_id'),
    re_path(r'^update_description_post/$', views.update_description_post, name='update_description_post'),

]