from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import mixins, viewsets

from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Read + create only. Posts are removed via the emailed link or by expiring."""

    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(
            is_verified=True,
            end_time__gt=timezone.now(),
        ).order_by("-created_at")

    def perform_create(self, serializer):
        session = serializer.save()
        base = settings.BACKEND_URL.rstrip("/")
        verify_url = f"{base}/verify/{session.verify_token}/"
        remove_url = f"{base}/remove/{session.verify_token}/"
        send_mail(
            subject="Verify your Ascend post",
            message=(
                f"Hi {session.display_name},\n\n"
                f"Click to confirm your study session and put it on the board:\n"
                f"{verify_url}\n\n"
                f"Leaving early? Remove your post any time:\n{remove_url}\n\n"
                "If you didn't post this, ignore this email."
            ),
            from_email=None,
            recipient_list=[session.email],
        )


def _frontend(query):
    return redirect(f"{settings.FRONTEND_URL.rstrip('/')}/?{query}")


def verify_session(request, token):
    session = get_object_or_404(Session, verify_token=token)
    if session.end_time <= timezone.now():
        return _frontend("expired=1")
    if not session.is_verified:
        session.is_verified = True
        session.save(update_fields=["is_verified"])
    return _frontend(f"verified={session.id}")


def remove_session(request, token):
    session = get_object_or_404(Session, verify_token=token)
    session.delete()
    return _frontend("removed=1")
