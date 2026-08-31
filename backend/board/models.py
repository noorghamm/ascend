from django.db import models

import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone


class Session(models.Model):
    ZONES = [
        ("green", "Green – group"),
        ("amber", "Amber – quiet"),
        ("red", "Red – silent"),
    ]

    email = models.EmailField()
    display_name = models.CharField(max_length=50)
    zone = models.CharField(max_length=5, choices=ZONES)
    level = models.PositiveSmallIntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    note = models.CharField(max_length=200, blank=True)
    contact = models.CharField(max_length=100, blank=True)

    is_verified = models.BooleanField(default=False)
    verify_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def is_active(self):
        return self.is_verified and self.end_time > timezone.now()

    def __str__(self):
        return f"{self.display_name} · {self.zone} · {self.start_time:%a %H:%M}"