from django.contrib import messages
from django.contrib.auth import logout as auth_logout


class SingleSessionMiddleware:
    """Enforces the 'One ID - One Device - One Login' policy: each account may
    have only one valid session at a time. Logging in on a new device marks that
    session as the account's active one (see views._bind_active_session); the
    next request from any other, now-stale session gets signed out here."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            current_key = request.session.session_key
            if user.active_session_key and current_key and user.active_session_key != current_key:
                auth_logout(request)
                messages.info(request, "You've been logged out because this account was signed in on another device.")
        return self.get_response(request)
