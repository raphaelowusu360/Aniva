"""
URL configuration for animehub project.
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Django admin
    path(
        'admin/',
        admin.site.urls
    ),


    # User system
    path(
        '',
        include('users.urls')
    ),


    # Chat system
    path(
        'chats/',
        include('chats.urls')
    ),

]


# Serve uploaded files (chat images, profile pictures, etc.)
# Only used during development
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
from users.views import reset_admin

urlpatterns = [
    path("reset-admin/", reset_admin),
]