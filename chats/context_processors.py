from .models import Message


def unread_messages(request):

    if request.user.is_authenticated:

        count = Message.objects.filter(
            chat__users=request.user,
            sender__isnull=False,
            is_read=False
        ).exclude(
            sender=request.user
        ).count()

        return {
            "unread_messages": count
        }


    return {
        "unread_messages": 0
    }