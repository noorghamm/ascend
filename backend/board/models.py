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

    # Which library levels belong to each zone. Used for validation and the UI.
    ZONE_LEVELS = {
        "group": [2, 3],
        "quiet": [1, 4, 5, 6, 7],
        "silent": [8, 9, 10, 11, 12],
    }

    email = models.EmailField()
    display_name = models.CharField(max_length=50)
    zone = models.CharField(max_length=6, choices=ZONES)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    end_time = models.DateTimeField(editable=False, null=True)
    note = models.CharField(max_length=200, blank=True)
    contact = models.CharField(max_length=100, blank=True)

    is_verified = models.BooleanField(default=False)
    verify_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # The board query: verified sessions that haven't ended yet.
            models.Index(fields=["is_verified", "end_time"], name="board_live_idx"),
            # Per-email lookups (one live post per email) and cleanup.
            models.Index(fields=["email", "end_time"], name="board_email_idx"),
        ]

    def save(self, *args, **kwargs):
        self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.is_verified and self.end_time > timezone.now()

    def __str__(self):
        return f"{self.display_name} · {self.zone} · {self.start_time:%a %H:%M}"
