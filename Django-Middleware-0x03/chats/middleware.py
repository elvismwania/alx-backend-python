from datetime import datetime, timedelta
from django.http import JsonResponse
import re


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = request.user if request.user.is_authenticated else "Anonymous"
        log_text = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        with open('./requests.log', 'a') as log:
            log.write(log_text)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        hour = datetime.now().hour
        restricted_hours = range(6, 9)

        is_conversation_route = (
            re.match(r"^/api/conversations", path) or
            re.match(r"^/api/users/\d+/conversations", path)
        )

        if is_conversation_route and hour in restricted_hours:
            return JsonResponse(
                {"detail": "Messaging is disabled during restricted hours (1AM-6AM)."},
                status=403
            )

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_log = {}  # IP: list of datetime objects

    def __call__(self, request):
        ip = self.get_ip(request)
        now = datetime.now()

        # Only apply to POST requests to message endpoints
        is_message_post = (
            request.method == "POST" and
            re.match(r"^/api/conversations/.*/messages/?", request.path)
        )

        if is_message_post:
            timestamps = self.message_log.get(ip, [])
            # Filter out timestamps older than 1 minute
            one_minute_ago = now - timedelta(minutes=1)
            timestamps = [t for t in timestamps if t > one_minute_ago]

            if len(timestamps) >= 5:
                return JsonResponse(
                    {"detail": "Rate limit exceeded: Max 5 messages per minute."},
                    status=429
                )

            timestamps.append(now)
            self.message_log[ip] = timestamps

        return self.get_response(request)

    def get_ip(self, request):
        """Get IP address from request headers (handle proxies too)."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_log = {}  # IP: list of datetime objects

    def __call__(self, request):
        role = request.user.role
        if role not in ['admin', 'host']:
            return JsonResponse({'detail': 'Guest not allowed.'}, status=403)

        return self.get_response(request)
