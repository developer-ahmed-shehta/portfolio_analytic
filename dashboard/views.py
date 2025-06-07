from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import Visitor, PageView, Event

from django.utils import timezone
from datetime import timedelta

def analytics_dashboard(request):
    # Time range handling (unchanged)
    time_range = request.GET.get('time_range', '24h')
    now = timezone.now()
    time_ranges = {
        '24h': now - timedelta(hours=24),
        '7d': now - timedelta(days=7),
        '30d': now - timedelta(days=30),
        'all': None
    }
    filter_date = time_ranges.get(time_range)

    # Base querysets
    visitor_queryset = Visitor.objects.all()
    pageview_queryset = PageView.objects.all()
    event_queryset = Event.objects.all()

    # Apply time filters
    if filter_date:
        visitor_queryset = visitor_queryset.filter(last_seen__gte=filter_date)
        pageview_queryset = pageview_queryset.filter(timestamp__gte=filter_date)
        event_queryset = event_queryset.filter(timestamp__gte=filter_date)

    # Core metrics for the chart - using your actual event types
    event_counts = {
        # Navigation events
        'nav_events': event_queryset.filter(
            event_type__in=['nav_projects', 'nav_about', 'nav_experience', 'nav_skills', 'nav_contact']
        ).count(),

        # Form interactions
        'form_events': event_queryset.filter(
            event_type__in=['contact_form_submit', 'contact_submit_button']
        ).count(),

        # Project views
        'project_events': event_queryset.filter(
            event_type__startswith='project_'
        ).count(),

        # Resume downloads
        'download_events': event_queryset.filter(
            event_type='nav_resume_download'
        ).count()
    }

    context = {
        'time_range': time_range,

        # Visitor metrics (unchanged)
        'total_visitors': visitor_queryset.count(),

        # Page view metrics (unchanged)
        'total_page_views': pageview_queryset.count(),
        'avg_session_duration': pageview_queryset.aggregate(
            avg_duration=Avg('duration'))['avg_duration'],

        # Event metrics (updated)
        'total_events': event_queryset.count(),
        'event_counts': event_counts,  # For the chart
        'event_types': event_queryset.values('event_type')
        .annotate(count=Count('event_type'))
        .order_by('-count'),

        # Recent data (unchanged)
        'recent_visitors': visitor_queryset.prefetch_related('pageview_set').order_by('-timestamp')[:10],
        'recent_events': event_queryset.order_by('-timestamp')[:10],
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


@csrf_exempt  # You might want proper CSRF protection for production
def update_page_view_duration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            page_view_id = data.get('page_view_id')
            duration = float(data.get('duration', 0))

            print("page_view_id", "duration")
            print(page_view_id,duration)
            try:
                page_view = PageView.objects.get(id=page_view_id)
                page_view.duration = duration
                page_view.save()
                return JsonResponse({'status': 'success'})
            except PageView.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'PageView not found'}, status=404)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)