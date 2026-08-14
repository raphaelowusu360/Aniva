from django.contrib import admin
from .models import Group, GroupPost

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "creator", "created_at")
    search_fields = ("name", "creator__username")
    list_filter = ("created_at",)

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ("group", "author", "created_at")
    search_fields = ("group__name", "author__username")
    list_filter = ("created_at",)


from django.contrib import admin
from .models import FeatureFeedback, FeedbackReaction


@admin.register(FeatureFeedback)
class FeatureFeedbackAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "feature_request",
        "created_at",
    )

    search_fields = (
        "user__username",
        "feature_request",
        "likes_about_site",
    )

    ordering = (
        "-created_at",
    )


@admin.register(FeedbackReaction)
class FeedbackReactionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "feedback",
        "reaction",
        "created_at",
    )

    list_filter = (
        "reaction",
    )