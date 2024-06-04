from django.urls import re_path

from Posts import views

urlpatterns = [
    # admin use
    re_path(r'^get_all_posts/$', views.get_all_posts, name='get_all_posts'),
    re_path(r"^get_unapproved_posts/$", views.get_unapproved_posts, name="get_unapproved_posts"),
    
    # general operation on posts 
    re_path(r'^add_post/$', views.add_post, name='add_post'), 
    re_path(r'^delete_post/$', views.delete_post, name='delete_post'),
    
    # getting operation on posts
    re_path(r'^get_post_by_post_id/$', views.get_post_by_post_id, name='get_post_by_post_id'), 
    re_path(r"^get_approved_posts/$", views.get_approved_posts, name="get_approved_posts"),
    re_path(r'^get_all_user_posts/$', views.get_all_user_posts, name='get_all_user_posts'),
    
    # updated things in post
    re_path(r'^update_post_review/$', views.update_post_review, name='update_post_review'),
    re_path(r"^fix_post_issues/$",views.fix_post_issues,name='fix_post_issues'),
    re_path(r"^update_aprtemanet_pics/$",views.update_apartment_pics,name='update_aprtemanet_pics'),

    # search post
    re_path(r"^get_post_by_parameters/$", views.get_post_by_parameters, name="get_post_by_parm"),
]