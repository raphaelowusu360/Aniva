from django.utils import timezone


class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                profile.last_seen = timezone.now()
                profile.save(update_fields=["last_seen"])
            except Exception:
                pass

        response = self.get_response(request)
        return response