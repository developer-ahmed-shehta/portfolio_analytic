from django.contrib import admin
from django.contrib.auth.models import User

from .models import *


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'timestamp', 'last_seen')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    pass