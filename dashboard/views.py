from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import Visitor, PageView, Event

from django.utils import timezone
from datetime import timedelta


def analytics_dashboard(request):
    # Get the selected time range from request (default to '24h')
    time_range = request.GET.get('time_range', '24h')

    # Define the time ranges and their corresponding datetime filters
    now = timezone.now()
    time_ranges = {
        '24h': now - timedelta(hours=24),
        '7d': now - timedelta(days=7),
        '30d': now - timedelta(days=30),
        'all': None  # Special case for "All Time"
    }

    # Get the filter datetime for the selected range
    filter_date = time_ranges.get(time_range)

    # Create base querysets
    visitor_queryset = Visitor.objects.all()
    pageview_queryset = PageView.objects.all()
    event_queryset = Event.objects.all()

    # Apply time filter if not "All Time"
    if filter_date:
        visitor_queryset = visitor_queryset.filter(timestamp__gte=filter_date)
        pageview_queryset = pageview_queryset.filter(timestamp__gte=filter_date)
        event_queryset = event_queryset.filter(timestamp__gte=filter_date)

    context = {
        'time_range': time_range,

        # Visitor metrics
        'total_visitors': visitor_queryset.count(),
        'unique_visitors': visitor_queryset.values('ip_address').distinct().count(),
        'returning_visitors': visitor_queryset.values('ip_address')
        .annotate(count=Count('ip_address'))
        .filter(count__gt=1).count(),

        # Page view metrics
        'total_page_views': pageview_queryset.count(),
        'avg_session_duration': pageview_queryset.aggregate(
            avg_duration=Avg('duration'))['avg_duration'],

        # Event metrics
        'total_events': event_queryset.count(),
        'event_types': event_queryset.values('event_type')
        .annotate(count=Count('event_type'))
        .order_by('-count'),

        # Recent data
        'recent_visitors': visitor_queryset.prefetch_related('pageview_set').order_by('-timestamp')[:10],
        'recent_events': event_queryset.order_by('-timestamp')[:10],

        # Device breakdown
        'device_distribution': visitor_queryset.values('device_type')
        .annotate(count=Count('device_type'))
        .order_by('-count'),
    }

    return render(request, 'analytics/dashboard.html', context)

@require_POST
def track_event(request):
    try:
        data = json.loads(request.body)
        print(data)
        # Get visitor IP (even if behind proxy)
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        visitor = Visitor.objects.filter(ip_address=ip).order_by('-timestamp').first()

        Event.objects.create(
            visitor=visitor,
            event_type=data.get('event_type'),
            page_url=data.get('page_url'),
            element_id=data.get('elementId'),
            element_class=data.get('elementClass'),
            element_text=data.get('elementText'),
            metadata=data.get('metadata')
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def track_pageview(request):
    try:
        data = json.loads(request.body)
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        # Create or update visitor
        visitor, created = Visitor.objects.get_or_create(
            ip_address=ip[:15] + '...' if len(ip) > 15 else ip,
            defaults={
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': data.get('referrer'),
                'landing_page': data.get('url')
            }
        )

        # Record page view
        PageView.objects.create(
            visitor=visitor,
            url=data.get('url'),
            referrer=data.get('referrer')
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
