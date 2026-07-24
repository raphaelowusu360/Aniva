# chats/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Chat, Message



@login_required
def chat_list(request):
    """
    Display all conversations belonging to the logged-in user.
    """

    chats = (
        Chat.objects
        .filter(users=request.user)
        .prefetch_related(
            'messages',
            'users'
        )
        .distinct()
    )

    return render(
        request,
        'chat/chat_list.html',
        {
            'chats': chats
        }
    )



@login_required
def chat_detail(request, user_id):
    """
    Open a conversation with another user and send messages.
    """

    other_user = get_object_or_404(
        User,
        id=user_id
    )


    # Find existing chat between the two users
    chat = (
        Chat.objects
        .filter(users=request.user)
        .filter(users=other_user)
        .first()
    )


    # Create chat if it does not exist
    if not chat:

        chat = Chat.objects.create()

        chat.users.add(
            request.user,
            other_user
        )



    # Send message
    if request.method == "POST":

        content = request.POST.get(
            'content',
            ''
        ).strip()


        image = request.FILES.get(
            'image'
        )


        if content or image:

            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content,
                image=image
            )


        return redirect(
            'chat_detail',
            user_id=other_user.id
        )



    # Mark messages from the other user as read
    chat.messages.filter(
        sender=other_user,
        is_read=False
    ).update(
        is_read=True
    )



    # Load messages
    messages = (
        chat.messages
        .select_related(
            'sender'
        )
        .order_by(
            'timestamp'
        )
    )


    return render(
        request,
        'chat/chat_detail.html',
        {
            'chat': chat,
            'other_user': other_user,
            'messages': messages
        }
    )




@login_required
def delete_chat_message(request, message_id):
    """
    Delete only messages sent by the logged-in user.
    """

    message = get_object_or_404(
        Message,
        id=message_id,
        sender=request.user
    )


    other_user = (
        message.chat.users
        .exclude(
            id=request.user.id
        )
        .first()
    )


    message.delete()


    return redirect(
        'chat_detail',
        user_id=other_user.id
    )