from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from board.models import Session


class Command(BaseCommand):
    help = "Delete expired sessions and stale unverified posts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-days", type=int, default=7,
            help="Keep expired sessions this many days (default 7).",
        )

    def handle(self, *args, **opts):
        now = timezone.now()
        expired, _ = Session.objects.filter(
            end_time__lt=now - timedelta(days=opts["keep_days"])
        ).delete()
        stale, _ = Session.objects.filter(
            is_verified=False, created_at__lt=now - timedelta(hours=24)
        ).delete()
        self.stdout.write(f"Deleted {expired} expired and {stale} stale unverified sessions.")
