from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ==========================
    #           HOME
    # ==========================
    path('', views.home, name='home'),

    # ==========================
    #           AUTH
    # ==========================
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='users/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    path('register/', views.register, name='register'),

    # ==========================
    #        USER PROFILE
    # ==========================
    path('profile/', views.profile, name='profile'),
    path('users/<str:username>/', views.public_profile, name='public_profile'),

    # ==========================
    #        ANIME PAGES
    # ==========================
    path('anime/', views.anime_list, name='anime_list'),
    path('favorites/', views.favorites, name='favorites'),

    # ==========================
    #        FRIEND SYSTEM
    # ==========================
    path('friends/', views.friends_list, name='friends_list'),
    path('friend-requests/', views.friend_requests_list, name='friend_requests_list'),
    path('send-friend/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('browse-users/', views.browse_users, name='browse_users'),


    # ==========================
    #        GROUP SYSTEM
    # ==========================
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/post/', views.add_group_post, name='add_group_post'), # <--- fixed
    path('feedback/', views.feature_feedback, name='feature_feedback'),
    path('groups/posts/<int:post_id>/delete/', views.delete_group_post, name='delete_group_post'),
    path('groups/post/<int:post_id>/edit/', views.edit_group_post, name='edit_group_post'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),

]
