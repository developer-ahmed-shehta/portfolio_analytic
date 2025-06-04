from django.urls import path
from . import views

urlpatterns = [
    path('analytics', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/track-event/', views.track_event, name='track_event'),
    path('analytics/track-pageview/', views.track_pageview, name='track_pageview'),

    path('analytic/', views.analytics_dashboard),
]