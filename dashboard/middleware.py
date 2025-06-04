from django.utils import timezone
from .models import Visitor, PageView
import user_agents
import socket
import json


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tracking for admin and static files
        if not self.should_track(request):
            return self.get_response(request)

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        # Parse user agent
        user_agent_str = request.META.get('HTTP_USER_AGENT', '')
        ua = user_agents.parse(user_agent_str)

        # Get or create visitor
        visitor, created = Visitor.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={
                'ip_address': self.get_client_ip(request),
                'user_agent': user_agent_str,
                'referrer': request.META.get('HTTP_REFERER', '')[:200],  # Truncate to fit URLField
                'landing_page': request.build_absolute_uri()[:200],  # Truncate to fit URLField
                'device_type': self.get_device_type(ua),
                'browser': ua.browser.family[:50],  # Truncate to fit CharField
                'os': ua.os.family[:50],  # Truncate to fit CharField
                'country': self.get_country(request),  # You'll need to implement this
            }
        )

        # Update last_seen and potentially other fields for existing visitors
        if not created:
            visitor.last_seen = timezone.now()

            # Update these fields if they're empty or you want to refresh them
            if not visitor.device_type:
                visitor.device_type = self.get_device_type(ua)
            if not visitor.browser:
                visitor.browser = ua.browser.family[:50]
            if not visitor.os:
                visitor.os = ua.os.family[:50]

            visitor.save()

        # Track page view
        PageView.objects.create(
            visitor=visitor,
            url=request.build_absolute_uri()[:200],
            referrer=request.META.get('HTTP_REFERER', '')[:200]
        )

        response = self.get_response(request)
        return response

    def should_track(self, request):
        excluded_paths = ['/admin/', '/static/', '/media/', '/analytic/']
        return not any(request.path.startswith(path) for path in excluded_paths)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_device_type(self, ua):
        if ua.is_mobile: return 'mobile'
        if ua.is_tablet: return 'tablet'
        if ua.is_pc: return 'desktop'
        if ua.is_bot: return 'bot'
        return 'other'

    def get_country(self, request):
        """
        Implement country detection based on IP
        Options:
        1. Use a geoip database (like GeoLite2)
        2. Use a third-party API
        3. Return None if not implemented
        """
        return None  # Implement your country detection logic here