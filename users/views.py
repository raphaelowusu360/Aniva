from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages

from .models import Profile, FriendRequest, get_friends, Group, GroupPost
from .forms import ProfileForm, GroupForm, GroupPostForm

# ==========================
#           HOME
# ==========================
def home(request):
    return render(request, "users/home.html")

# ==========================
#        AUTH SYSTEM
# ==========================
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = UserCreationForm()
    return render(request, "users/register.html", {"form": form})

# ==========================
#        USER PROFILE
# ==========================
@login_required
def profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "users/profile.html", {"profile": profile, "form": form})

@login_required
def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = getattr(user, "profile", None)

    is_friend = FriendRequest.objects.filter(
        (Q(sender=request.user) & Q(receiver=user) & Q(accepted=True)) |
        (Q(sender=user) & Q(receiver=request.user) & Q(accepted=True))
    ).exists()

    request_sent = FriendRequest.objects.filter(sender=request.user, receiver=user, accepted=False).exists()
    request_received = FriendRequest.objects.filter(sender=user, receiver=request.user, accepted=False).exists()

    return render(request, "users/public_profile.html", {
        "profile_user": user,
        "profile": profile,
        "is_friend": is_friend,
        "request_sent": request_sent,
        "request_received": request_received,
    })

# ==========================
#        ANIME PAGES
# ==========================
@login_required
def anime_list(request):
    return render(request, "users/anime_list.html")

@login_required
def favorites(request):
    return render(request, "users/favorites.html")

# ==========================
#        FRIEND SYSTEM
# ==========================
@login_required
def friends_list(request):
    friends = get_friends(request.user)
    return render(request, 'users/friends_list.html', {'friends': friends})

@login_required
def friend_requests_list(request):
    requests = FriendRequest.objects.filter(receiver=request.user, accepted=False)
    return render(request, 'users/friend_requests_list.html', {'requests': requests})

@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if receiver != request.user:
        FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    return redirect("public_profile", username=receiver.username)

@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id)
    if fr.receiver == request.user:
        fr.accepted = True
        fr.save()
    return redirect("friend_requests_list")

@login_required
def decline_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id)
    if fr.receiver == request.user:
        fr.delete()
    return redirect("friend_requests_list")

@login_required
def remove_friend(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    fr = FriendRequest.objects.filter(
        (Q(sender=request.user) & Q(receiver=friend) & Q(accepted=True)) |
        (Q(sender=friend) & Q(receiver=request.user) & Q(accepted=True))
    ).first()
    if fr:
        fr.delete()
    return redirect("friends_list")

# ==========================
#        GROUP SYSTEM
# ==========================
@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'users/group_list.html', {'groups': groups})

@login_required
def groups_list(request):  # optional, can remove if unused
    groups = Group.objects.all()
    return render(request, 'users/groups_list.html', {'groups': groups})

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)  # Creator is a member
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'users/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    posts = group.posts.all().order_by('-created_at')

    form = GroupPostForm()
    return render(request, 'users/group_detail.html', {
        'group': group,
        'posts': posts,
        'form': form
    })

@login_required
def add_group_post(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # ✅ Only allow members to post
    if request.user not in group.members.all():
        messages.error(request, "You must join this group before posting.")
        return redirect('group_detail', group_id=group.id)

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            GroupPost.objects.create(
                group=group,
                author=request.user,
                content=content
            )
            messages.success(request, "Your post has been added successfully!")
        else:
            messages.error(request, "Post content cannot be empty.")
        
        return redirect('group_detail', group_id=group.id)  # ✅ Must return something here

    # Optionally handle GET request if needed
    return redirect('group_detail', group_id=group.id)

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.user)
    return redirect('group_detail', group_id=group.id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.remove(request.user)
    return redirect('group_list')
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField

@login_required
def browse_users(request):
    current_user = request.user
    my_country = current_user.profile.country

    users = (
        User.objects
        .exclude(id=current_user.id)
        .annotate(
            country_priority=Case(
                When(profile__country=my_country, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by('country_priority', 'username')
    )

    return render(request, 'users/browse_users.html', {'users': users})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FeatureFeedback
from django.contrib.auth.decorators import login_required

@login_required
def feature_feedback(request):
    if request.method == "POST":
        feature = request.POST.get("feature")
        likes = request.POST.get("likes")
        if feature and likes:
            FeatureFeedback.objects.create(
                user=request.user,
                feature_request=feature,
                likes_about_site=likes
            )
            messages.success(request, "Feedback submitted successfully!")
            return redirect('feature_feedback')  # Redirect to same page

    feedbacks = FeatureFeedback.objects.all().order_by('-created_at')
    return render(request, 'users/feature_feedback.html', {'feedbacks': feedbacks})
@login_required
def delete_group_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    group = post.group

    # Permission check
    if request.user != post.author and request.user != group.creator:
        messages.error(request, "You do not have permission to delete this post.")
        return redirect('group_detail', group_id=group.id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")

    return redirect('group_detail', group_id=group.id)
@login_required
def edit_group_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    group = post.group

    # Only author or group creator can edit
    if request.user != post.author and request.user != group.creator:
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('group_detail', group_id=group.id)

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            post.content = content
            post.save()
            messages.success(request, "Post updated successfully.")
            return redirect('group_detail', group_id=group.id)
        else:
            messages.error(request, "Content cannot be empty.")

    return render(request, 'users/edit_group_post.html', {'post': post})
@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.creator:
        messages.error(request, "Only the group creator can delete this group.")
        return redirect('group_detail', group_id=group.id)

    if request.method == "POST":
        group.delete()
        messages.success(request, f"Group '{group.name}' deleted successfully.")
        return redirect('group_list')

    return render(request, 'users/delete_group_confirm.html', {'group': group})
from django.http import HttpResponse
from django.contrib.auth.models import User

def reset_admin(request):
    user = User.objects.get(username="raphaelowusu")
    user.set_password("NewPassword123!")
    user.save()

    return HttpResponse("Password reset")