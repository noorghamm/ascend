from django.contrib import admin

from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("display_name", "zone", "level", "start_time", "end_time", "is_verified", "email")
    list_filter = ("zone", "is_verified")
    search_fields = ("display_name", "email")
    readonly_fields = ("verify_token", "end_time", "created_at")
