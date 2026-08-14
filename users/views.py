from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Case, When, Value, IntegerField
from django.contrib import messages
from django.utils import timezone

from .models import (
    Profile,
    FriendRequest,
    Follow,
    get_friends,
    Group,
    GroupPost,
    FeatureFeedback,
    FeedbackReaction,
)

from .forms import (
    ProfileForm,
    GroupForm,
    GroupPostForm
)


# HOME

def home(request):
    return render(
        request,
        "users/home.html"
    )


# AUTH SYSTEM

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect("profile")

    else:
        form = UserCreationForm()

    return render(
        request,
        "users/register.html",
        {
            "form": form
        }
    )


# MY PROFILE

@login_required
def profile(request):
    profile = request.user.profile

    followers_count = Follow.objects.filter(
        following=request.user
    ).count()

    following_count = Follow.objects.filter(
        follower=request.user
    ).count()

    friends = User.objects.filter(
        followers__follower=request.user,
        following__following=request.user
    ).distinct().order_by("username")

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()

            return redirect("profile")

    else:
        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "users/profile.html",
        {
            "profile": profile,
            "form": form,
            "followers_count": followers_count,
            "following_count": following_count,
            "friends": friends,
        }
    )


# PUBLIC PROFILE

@login_required
def public_profile(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    profile = getattr(
        profile_user,
        "profile",
        None
    )

    is_online = False

    if profile and profile.last_seen:
        online_limit = timezone.now() - timedelta(minutes=5)

        is_online = profile.last_seen >= online_limit

    is_friend = FriendRequest.objects.filter(
        (
            Q(
                sender=request.user,
                receiver=profile_user,
                accepted=True
            )
        )
        |
        (
            Q(
                sender=profile_user,
                receiver=request.user,
                accepted=True
            )
        )
    ).exists()

    request_sent = FriendRequest.objects.filter(
        sender=request.user,
        receiver=profile_user,
        accepted=False
    ).exists()

    request_received = FriendRequest.objects.filter(
        sender=profile_user,
        receiver=request.user,
        accepted=False
    ).first()

    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    friends = get_friends(profile_user)

    return render(
        request,
        "users/public_profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "is_online": is_online,
            "is_friend": is_friend,
            "request_sent": request_sent,
            "request_received": request_received,
            "request_received_id":
                request_received.id
                if request_received
                else None,
            "is_following": is_following,
            "followers_count": followers_count,
            "following_count": following_count,
            "friends": friends,
        }
    )


# ANIME PAGES

@login_required
def anime_list(request):
    return render(
        request,
        "users/anime_list.html"
    )


@login_required
def favorites(request):
    return render(
        request,
        "users/favorites.html"
    )


# FRIEND SYSTEM

@login_required
def friends_list(request):
    friends = get_friends(
        request.user
    )

    return render(
        request,
        "users/friends_list.html",
        {
            "friends": friends
        }
    )

@login_required
def friend_requests_list(request):

    # People who follow the current user
    incoming_follows = Follow.objects.filter(
        following=request.user
    ).exclude(
        follower=request.user
    ).select_related(
        "follower",
        "follower__profile"
    ).order_by(
        "-created_at"
    )


    # People the current user already follows
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list(
        "following_id",
        flat=True
    )


    # Only show people who follow the user
    # but whom the user does NOT follow back
    follow_requests = incoming_follows.exclude(
        follower_id__in=following_ids
    )


    return render(
        request,
        "users/friend_requests_list.html",
        {
            "follow_requests": follow_requests,
        }
    )
@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(
        User,
        id=user_id
    )

    if receiver != request.user:
        FriendRequest.objects.get_or_create(
            sender=request.user,
            receiver=receiver,
            defaults={
                "accepted": False
            }
        )

    return redirect(
        "public_profile",
        username=receiver.username
    )


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
        accepted=False
    )

    friend_request.accepted = True
    friend_request.save()

    friend_request.sender.profile.friends.add(
        friend_request.receiver.profile
    )

    friend_request.receiver.profile.friends.add(
        friend_request.sender.profile
    )

    return redirect(
        "friend_requests_list"
    )


@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
        accepted=False
    )

    friend_request.delete()

    return redirect(
        "friend_requests_list"
    )


@login_required
def remove_friend(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id
    )

    request.user.profile.friends.remove(
        user.profile
    )

    user.profile.friends.remove(
        request.user.profile
    )

    return redirect(
        "friends_list"
    )


# GROUP SYSTEM

@login_required
def group_list(request):
    groups = Group.objects.all()

    return render(
        request,
        "users/group_list.html",
        {
            "groups": groups
        }
    )


@login_required
def groups_list(request):
    groups = Group.objects.all()

    return render(
        request,
        "users/groups_list.html",
        {
            "groups": groups
        }
    )


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(
            request.POST
        )

        if form.is_valid():
            group = form.save(
                commit=False
            )

            group.creator = request.user

            group.save()

            group.members.add(
                request.user
            )

            return redirect(
                "group_list"
            )

    else:
        form = GroupForm()

    return render(
        request,
        "users/create_group.html",
        {
            "form": form
        }
    )


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(
        Group,
        id=group_id
    )

    posts = group.posts.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "users/group_detail.html",
        {
            "group": group,
            "posts": posts,
            "form": GroupPostForm()
        }
    )


@login_required
def add_group_post(request, group_id):
    group = get_object_or_404(
        Group,
        id=group_id
    )

    if request.user not in group.members.all():
        messages.error(
            request,
            "You must join this group before posting."
        )

        return redirect(
            "group_detail",
            group_id=group.id
        )

    if request.method == "POST":
        content = request.POST.get(
            "content"
        )

        if content:
            GroupPost.objects.create(
                group=group,
                author=request.user,
                content=content
            )

        return redirect(
            "group_detail",
            group_id=group.id
        )

    return redirect(
        "group_detail",
        group_id=group.id
    )


# GROUP MEMBERS

@login_required
def join_group(request, group_id):
    group = get_object_or_404(
        Group,
        id=group_id
    )

    group.members.add(
        request.user
    )

    return redirect(
        "group_detail",
        group_id=group.id
    )


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(
        Group,
        id=group_id
    )

    group.members.remove(
        request.user
    )

    return redirect(
        "group_list"
    )


# BROWSE USERS

@login_required
def browse_users(request):
    current_user = request.user

    country = current_user.profile.country

    users = User.objects.exclude(
        id=current_user.id
    ).annotate(
        country_priority=Case(
            When(
                profile__country=country,
                then=Value(0)
            ),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by(
        "country_priority",
        "username"
    )

    return render(
        request,
        "users/browse_users.html",
        {
            "users": users
        }
    )


# -----------------------------
# Feature Feedback
# -----------------------------

@login_required
def feature_feedback(request):

    if request.method == "POST":

        feature = request.POST.get(
            "feature"
        )

        likes = request.POST.get(
            "likes"
        )

        if feature and likes:

            FeatureFeedback.objects.create(
                user=request.user,
                feature_request=feature,
                likes_about_site=likes
            )

            messages.success(
                request,
                "Feedback submitted successfully!"
            )

            return redirect(
                "feature_feedback"
            )

    feedbacks = FeatureFeedback.objects.all().order_by(
        "-created_at"
    )

    # Add separate reaction counts to each feedback
    for feedback in feedbacks:

        feedback.like_count = feedback.reactions.filter(
            reaction=FeedbackReaction.LIKE
        ).count()

        feedback.dislike_count = feedback.reactions.filter(
            reaction=FeedbackReaction.DISLIKE
        ).count()

    return render(
        request,
        "users/feature_feedback.html",
        {
            "feedbacks": feedbacks
        }
    )

# -----------------------------
# Feedback Reaction
# -----------------------------

@login_required
def react_to_feedback(request, feedback_id):

    if request.method == "POST":

        feedback = get_object_or_404(
            FeatureFeedback,
            id=feedback_id
        )

        reaction_type = request.POST.get(
            "reaction"
        )

        if reaction_type not in [
            FeedbackReaction.LIKE,
            FeedbackReaction.DISLIKE
        ]:
            return redirect(
                "feature_feedback"
            )

        existing_reaction = FeedbackReaction.objects.filter(
            user=request.user,
            feedback=feedback
        ).first()

        if existing_reaction:

            # Clicking the same reaction removes it
            if existing_reaction.reaction == reaction_type:

                existing_reaction.delete()

            # Clicking the opposite reaction switches it
            else:

                existing_reaction.reaction = reaction_type
                existing_reaction.save()

        else:

            FeedbackReaction.objects.create(
                user=request.user,
                feedback=feedback,
                reaction=reaction_type
            )

    return redirect(
        "feature_feedback"
    )


# GROUP POST MANAGEMENT

@login_required
def delete_group_post(request, post_id):
    post = get_object_or_404(
        GroupPost,
        id=post_id
    )

    group = post.group

    if request.user == post.author or request.user == group.creator:
        if request.method == "POST":
            post.delete()

    return redirect(
        "group_detail",
        group_id=group.id
    )


@login_required
def edit_group_post(request, post_id):
    post = get_object_or_404(
        GroupPost,
        id=post_id
    )

    group = post.group

    if request.user != post.author and request.user != group.creator:
        return redirect(
            "group_detail",
            group_id=group.id
        )

    if request.method == "POST":
        content = request.POST.get(
            "content"
        )

        if content:
            post.content = content

            post.save()

            return redirect(
                "group_detail",
                group_id=group.id
            )

    return render(
        request,
        "users/edit_group_post.html",
        {
            "post": post
        }
    )


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(
        Group,
        id=group_id
    )

    if request.user != group.creator:
        return redirect(
            "group_detail",
            group_id=group.id
        )

    if request.method == "POST":
        group.delete()

        return redirect(
            "group_list"
        )

    return render(
        request,
        "users/delete_group_confirm.html",
        {
            "group": group
        }
    )


# FOLLOW SYSTEM

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(
        User,
        id=user_id
    )

    if user_to_follow != request.user:
        Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect(
        "public_profile",
        username=user_to_follow.username
    )


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(
        User,
        id=user_id
    )

    Follow.objects.filter(
        follower=request.user,
        following=user_to_unfollow
    ).delete()

    return redirect(
        "public_profile",
        username=user_to_unfollow.username
    )


# FOLLOWERS / FOLLOWING

@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    followers = User.objects.filter(
        following__following=profile_user
    ).distinct().order_by(
        "username"
    )

    return render(
        request,
        "users/followers_list.html",
        {
            "profile_user": profile_user,
            "followers": followers,
        }
    )


@login_required
def following_list(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    following = User.objects.filter(
        followers__follower=profile_user
    ).distinct().order_by(
        "username"
    )

    return render(
        request,
        "users/following_list.html",
        {
            "profile_user": profile_user,
            "following": following,
        }
    )


# FOLLOW BACK

@login_required
def follow_back_user(request, user_id):
    user_to_follow = get_object_or_404(
        User,
        id=user_id
    )

    if user_to_follow != request.user:
        Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect(
        "friend_requests_list"
    )