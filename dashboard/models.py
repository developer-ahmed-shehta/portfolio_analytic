from django.db import models
from django.utils import timezone


class Visitor(models.Model):
    session_key = models.CharField(max_length=40,)

    ip_address = models.CharField(max_length=45)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    landing_page = models.URLField()
    last_seen = models.DateTimeField(auto_now=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.CharField(max_length=20, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Visitor'
        verbose_name_plural = 'Visitors'

    def __str__(self):
        return f"{self.ip_address} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class PageView(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'


class Event(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=20)
    element_id = models.CharField(max_length=100, null=True, blank=True)
    element_class = models.CharField(max_length=100, null=True, blank=True)
    element_text = models.TextField(null=True, blank=True)
    page_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"