# chat/urls.py

from django.urls import path
from . import views


urlpatterns = [

    # List all conversations
    path(
        '',
        views.chat_list,
        name='chat_list'
    ),


    # Open chat with a user
    path(
        '<int:user_id>/',
        views.chat_detail,
        name='chat_detail'
    ),


    # Delete a message
    path(
        'delete_message/<int:message_id>/',
        views.delete_chat_message,
        name='delete_chat_message'
    ),

]