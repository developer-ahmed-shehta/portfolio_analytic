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


def get_time_range_filter(time_range):
    """Handle time range selection and return filter date"""
    now = timezone.now()
    time_ranges = {
        '24h': now - timedelta(hours=24),
        '7d': now - timedelta(days=7),
        '30d': now - timedelta(days=30),
        'all': None
    }
    return time_ranges.get(time_range)


def get_filtered_querysets(filter_date):
    """Return filtered querysets based on time range"""
    visitor_queryset = Visitor.objects.all()
    pageview_queryset = PageView.objects.all()
    event_queryset = Event.objects.all()

    if filter_date:
        visitor_queryset = visitor_queryset.filter(last_seen__gte=filter_date)
        pageview_queryset = pageview_queryset.filter(timestamp__gte=filter_date)
        event_queryset = event_queryset.filter(timestamp__gte=filter_date)

    return visitor_queryset, pageview_queryset, event_queryset


def get_event_counts(event_queryset):
    """Calculate counts for different event types"""
    return {
        'nav_events': event_queryset.filter(
            event_type__in=['nav_projects', 'nav_about', 'nav_experience',
                            'nav_skills', 'nav_contact']
        ).count(),
        'form_events': event_queryset.filter(
            event_type__in=['contact_form_submit', 'contact_submit_button']
        ).count(),
        'project_events': event_queryset.filter(
            event_type__startswith='project_'
        ).count(),
        'download_events': event_queryset.filter(
            event_type='nav_resume_download'
        ).count()
    }


def get_visitor_trends(time_range, visitor_queryset):
    """Generate visitor trends data based on time range"""
    visitor_trends = []
    now = timezone.now()

    if time_range == '24h':
        # Hourly data for 24 hours
        for i in range(24, 0, -1):
            time_start = now - timedelta(hours=i)
            time_end = now - timedelta(hours=i - 1)
            count = visitor_queryset.filter(
                last_seen__gte=time_start,
                last_seen__lt=time_end
            ).count()
            visitor_trends.append({
                'label': time_start.strftime('%H:00'),
                'count': count
            })
    elif time_range in ['7d', '30d']:
        # Daily data
        days = 7 if time_range == '7d' else 30
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            count = visitor_queryset.filter(
                last_seen__year=date.year,
                last_seen__month=date.month,
                last_seen__day=date.day
            ).count()
            visitor_trends.append({
                'label': date.strftime('%b %d'),
                'count': count
            })
    else:  # 'all' time
        # Weekly data (last 12 weeks)
        for i in range(12, 0, -1):
            week_start = now - timedelta(weeks=i)
            week_end = now - timedelta(weeks=i - 1)
            count = visitor_queryset.filter(
                last_seen__gte=week_start,
                last_seen__lt=week_end
            ).count()
            visitor_trends.append({
                'label': f"Week {week_start.isocalendar().week}",
                'count': count
            })

    return visitor_trends


def analytics_dashboard(request):
    """Main dashboard view - now much cleaner"""
    time_range = request.GET.get('time_range', '24h')
    filter_date = get_time_range_filter(time_range)

    visitor_queryset, pageview_queryset, event_queryset = get_filtered_querysets(filter_date)
    event_counts = get_event_counts(event_queryset)
    visitor_trends = get_visitor_trends(time_range, visitor_queryset)

    context = {
        'time_range': time_range,
        'total_visitors': visitor_queryset.count(),
        'total_page_views': pageview_queryset.count(),
        'avg_session_duration': pageview_queryset.aggregate(
            avg_duration=Avg('duration'))['avg_duration'],
        'total_events': event_queryset.count(),
        'event_counts': event_counts,
        'event_types': event_queryset.values('event_type')
        .annotate(count=Count('event_type'))
        .order_by('-count'),
        'recent_visitors': visitor_queryset.prefetch_related('pageview_set')
                           .order_by('-timestamp')[:10],
        'recent_events': event_queryset.order_by('-timestamp')[:10],
        'visitor_trends': visitor_trends,
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