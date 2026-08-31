import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone


class Session(models.Model):
    ZONES = [
        ("group", "Group study (green, levels 2–3)"),
        ("quiet", "Quiet study (amber, levels 1, 4–7)"),
        ("silent", "Silent study (red, levels 8–12)"),
    ]

    email = models.EmailField()
    display_name = models.CharField(max_length=50)
    zone = models.CharField(max_length=6, choices=ZONES)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    end_time = models.DateTimeField(editable=False, null=True)   # NEW: real column
    note = models.CharField(max_length=200, blank=True)
    contact = models.CharField(max_length=100, blank=True)

    is_verified = models.BooleanField(default=False)
    verify_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):                             # NEW
        self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    @property
    def is_active(self):                                         # kept, unchanged
        return self.is_verified and self.end_time > timezone.now()

    def __str__(self):
        return f"{self.display_name} · {self.zone} · {self.start_time:%a %H:%M}"