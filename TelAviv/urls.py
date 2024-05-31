from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls import include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^', include('Users.urls')),
    re_path(r'^', include('Posts.urls')),
    re_path(r'^',include('Inbox.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    