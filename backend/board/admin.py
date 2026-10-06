from datetime import timedelta

from django.contrib import admin
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate, ExtractHour
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("display_name", "zone", "level", "start_time", "end_time", "is_verified", "email")
    list_filter = ("zone", "is_verified")
    search_fields = ("display_name", "email")
    readonly_fields = ("verify_token", "end_time", "created_at")

    def get_urls(self):
        return [
            path("stats/", self.admin_site.admin_view(self.stats_view), name="board_session_stats"),
        ] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), "show_stats_link": True}
        return super().changelist_view(request, extra_context)

    def stats_view(self, request):
        now = timezone.now()
        since = now - timedelta(days=30)
        recent = Session.objects.filter(created_at__gte=since)

        total = recent.count()
        verified = recent.filter(is_verified=True).count()

        per_day = list(
            recent.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(posts=Count("id"), verified=Count("id", filter=Q(is_verified=True)))
            .order_by("-day")
        )
        per_zone = list(
            recent.filter(is_verified=True)
            .values("zone")
            .annotate(posts=Count("id"), avg_minutes=Avg("duration_minutes"))
            .order_by("-posts")
        )
        zone_labels = dict(Session.ZONES)
        for row in per_zone:
            row["label"] = zone_labels.get(row["zone"], row["zone"])
            row["avg_minutes"] = round(row["avg_minutes"] or 0)

        per_hour = {
            r["hour"]: r["posts"]
            for r in recent.filter(is_verified=True)
            .annotate(hour=ExtractHour("start_time"))
            .values("hour")
            .annotate(posts=Count("id"))
        }
        hours = [{"hour": h, "posts": per_hour.get(h, 0)} for h in range(24)]
        peak = max(per_hour.values(), default=0)
        for h in hours:
            h["pct"] = round(100 * h["posts"] / peak) if peak else 0

        context = {
            **self.admin_site.each_context(request),
            "title": "Ascend stats (last 30 days)",
            "live_now": Session.objects.filter(is_verified=True, end_time__gt=now).count(),
            "total": total,
            "verified": verified,
            "verify_rate": round(100 * verified / total) if total else 0,
            "unique_emails": recent.filter(is_verified=True).values("email").distinct().count(),
            "per_day": per_day,
            "per_zone": per_zone,
            "hours": hours,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/board/session/stats.html", context)
