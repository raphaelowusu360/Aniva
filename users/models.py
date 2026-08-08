from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


# -----------------------------
# Profile Model
# -----------------------------
class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    favourite_anime = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        default="default.jpg"
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    friends = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True
    )

    # Updates whenever profile is saved
    last_seen = models.DateTimeField(
        auto_now=True
    )

    @property
    def is_online(self):

        if self.last_seen:
            return timezone.now() - self.last_seen < timedelta(minutes=5)

        return False

    def __str__(self):
        return f"{self.user.username}'s Profile"


# -----------------------------
# Profile Signals
# -----------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(
            user=instance
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):

    try:
        instance.profile.save()

    except Profile.DoesNotExist:
        Profile.objects.create(
            user=instance
        )


# -----------------------------
# Friend Requests
# -----------------------------
class FriendRequest(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_requests"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_requests"
    )

    accepted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"


# -----------------------------
# Followers System
# -----------------------------
class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "follower",
            "following",
        )

    def __str__(self):

        return (
            f"{self.follower.username} "
            f"follows {self.following.username}"
        )


# -----------------------------
# Get Mutual Friends
# -----------------------------
def get_friends(user):

    following_ids = Follow.objects.filter(
        follower=user
    ).values_list(
        "following_id",
        flat=True
    )

    followers_ids = Follow.objects.filter(
        following=user
    ).values_list(
        "follower_id",
        flat=True
    )

    mutual_friend_ids = set(following_ids).intersection(
        set(followers_ids)
    )

    return User.objects.filter(
        id__in=mutual_friend_ids
    )


# -----------------------------
# Communities / Groups
# -----------------------------
class Group(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_groups"
    )

    members = models.ManyToManyField(
        User,
        related_name="community_groups",
        blank=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return self.name


# -----------------------------
# Group Posts
# -----------------------------
class GroupPost(models.Model):

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Post by {self.author.username} in {self.group.name}"


# -----------------------------
# Feature Feedback
# -----------------------------
class FeatureFeedback(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )

    feature_request = models.TextField()

    likes_about_site = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"Feedback from {self.user.username} "
            f"on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )