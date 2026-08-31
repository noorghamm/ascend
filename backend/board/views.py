from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets

from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(
            is_verified=True,
            end_time__gt=timezone.now(),
        ).order_by("start_time")

    def perform_create(self, serializer):
        session = serializer.save()
        verify_url = f"http://127.0.0.1:8000/verify/{session.verify_token}/"
        send_mail(
            subject="Verify your Ascend post",
            message=(
                f"Hi {session.display_name},\n\n"
                f"Click to confirm your study session:\n{verify_url}\n\n"
                "If you didn't post this, ignore this email."
            ),
            from_email=None,
            recipient_list=[session.email],
        )


def verify_session(request, token):
    session = get_object_or_404(Session, verify_token=token)
    session.is_verified = True
    session.save()
    return HttpResponse("Verified! Your session is now live on the board.")