

import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden
from django.http import HttpResponseTooManyRequests



# Configure logger (writes to requests.log)
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)



class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response



class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define allowed time window (6 PM to 9 PM)
        allowed_start = time(18, 0)  # 6:00 PM
        allowed_end = time(21, 0)    # 9:00 PM
        now = datetime.now().time()

        if not (allowed_start <= now <= allowed_end):
            return HttpResponseForbidden("Access to chat is restricted between 6 PM and 9 PM only.")

        return self.get_response(request)



# Memory-based IP tracking (not suitable for multi-server or production)
ip_request_log = {}

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 5  # Max 5 messages
        self.time_window = 60  # In seconds

    def __call__(self, request):
        # Only rate-limit POST requests (typically chat messages)
        if request.method == "POST":
            ip = self.get_client_ip(request)
            now = time.time()

            # Initialize log for IP
            if ip not in ip_request_log:
                ip_request_log[ip] = []

            # Remove timestamps older than time_window
            ip_request_log[ip] = [
                timestamp for timestamp in ip_request_log[ip]
                if now - timestamp < self.time_window
            ]

            # Check rate limit
            if len(ip_request_log[ip]) >= self.rate_limit:
                return HttpResponseTooManyRequests("Rate limit exceeded: Max 5 messages per minute.")

            # Record this request
            ip_request_log[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip



class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_roles = ['admin', 'moderator']

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            user_role = getattr(user, 'role', None)
            if user_role not in self.allowed_roles:
                return HttpResponseForbidden("Access denied: Insufficient role permissions.")
        else:
            return HttpResponseForbidden("Access denied: User is not authenticated.")

        return self.get_response(request)
