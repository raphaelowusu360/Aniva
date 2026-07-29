"""
URL configuration for animehub project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import reset_admin  # Temporary - remove after admin login works

urlpatterns = [
    # Django admin
    path(
        "admin/",
        admin.site.urls,
    ),

    # User system
    path(
        "",
        include("users.urls"),
    ),

    # Chat system
    path(
        "chats/",
        include("chats.urls"),
    ),

    # Temporary password reset endpoint
    path(
        "reset-admin/",
        reset_admin,
    ),
]

# Serve uploaded files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )