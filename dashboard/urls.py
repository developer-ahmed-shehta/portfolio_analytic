from django.urls import path
from . import views

urlpatterns = [
    path('analytics', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/track-event/', views.track_event, name='track_event'),
    path('analytics/update-duration/', views.update_page_view_duration, name='update_page_view_duration'),

    path('analytic/', views.analytics_dashboard),
]