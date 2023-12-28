from django.urls import re_path

from Posts import views

urlpatterns = [
    # Attach the right function to the right url
    re_path(r'^add_post/$', views.add_post, name='add_post'), 
    re_path(r'^feed_posts/$', views.get_all_posts, name='get_all_posts'),
    re_path(r'^get_post/$', views.get_post_by_post_id, name='get_post'), 
    re_path(r'^get_post_by_user_id/$', views.get_post_by_user_id, name='get_post_by_user_id'),
    re_path(r'^update_description_post/$', views.update_description_post, name='update_description_post'),
    re_path(r'^delete_post/$', views.delete_post, name='delete_post'),
    re_path(r"^get_post_by_parm/$", views.get_post_by_parm, name="get_post_by_parm"),
    re_path(r"^get_all_posts_zero_status/$", views.get_all_posts_zero_status, name="get_all_posts_zero_status"),
]