"""Django email backend that sends through the Resend HTTP API.

Selected automatically when RESEND_API_KEY is set. Uses only the standard
library so there's nothing extra to install.
"""
import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

API_URL = "https://api.resend.com/emails"


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sent = 0
        for msg in email_messages:
            payload = {
                "from": msg.from_email or settings.DEFAULT_FROM_EMAIL,
                "to": list(msg.to),
                "subject": msg.subject,
                "text": msg.body,
            }
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode(),
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as res:
                    if 200 <= res.status < 300:
                        sent += 1
            except (urllib.error.URLError, TimeoutError) as exc:
                if not self.fail_silently:
                    raise
                # fail_silently: swallow but don't count as sent.
                _ = exc
        return sent
