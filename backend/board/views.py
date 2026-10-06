from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Read + create, plus owner-only `leave` and `extend` actions.

    The create response includes `owner_key` (the post's verify token). The
    browser keeps it so the poster can end or extend their post from the UI
    without the email. It is never returned by list or retrieve.
    """

    serializer_class = SessionSerializer
    MAX_MINUTES = 360
    EXTEND_STEP = 30

    def get_queryset(self):
        return Session.objects.filter(
            is_verified=True,
            end_time__gt=timezone.now(),
        ).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        res.data["owner_key"] = str(Session.objects.get(pk=res.data["id"]).verify_token)
        return res

    def _owned(self, request):
        """Return the live session for this id if the request carries its key."""
        session = get_object_or_404(Session, pk=self.kwargs["pk"], is_verified=True)
        key = str(request.data.get("owner_key", ""))
        if key != str(session.verify_token):
            return None
        return session

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        session = self._owned(request)
        if session is None:
            return Response({"detail": "Not your post."}, status=status.HTTP_403_FORBIDDEN)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def extend(self, request, pk=None):
        session = self._owned(request)
        if session is None:
            return Response({"detail": "Not your post."}, status=status.HTTP_403_FORBIDDEN)
        now = timezone.now()
        if session.end_time <= now:
            return Response({"detail": "That post has already ended."}, status=status.HTTP_400_BAD_REQUEST)
        # Extend from the current end, capped by total duration from the start.
        new_end = session.end_time + timedelta(minutes=self.EXTEND_STEP)
        total = int((new_end - session.start_time).total_seconds() // 60)
        if total > self.MAX_MINUTES:
            return Response(
                {"detail": f"Posts can't run longer than {self.MAX_MINUTES // 60} hours."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.duration_minutes = total
        session.save()
        return Response(self.get_serializer(session).data)

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
