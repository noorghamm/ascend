from django.conf import settings
from datetime import timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Session


def payload(**overrides):
    base = {
        "email": "abc123x@student.gla.ac.uk",
        "display_name": "Noor",
        "zone": "group",
        "level": 2,
        "start_time": timezone.now().isoformat(),
        "duration_minutes": 60,
        "note": "CS1F past papers",
        "contact": "@noor",
    }
    base.update(overrides)
    return base


class CreateSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_sends_verify_and_remove_links(self):
        res = self.client.post("/api/sessions/", payload(), format="json")
        self.assertEqual(res.status_code, 201)
        session = Session.objects.get()
        self.assertFalse(session.is_verified)
        self.assertEqual(session.end_time, session.start_time + timedelta(minutes=60))
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn(f"/verify/{session.verify_token}/", body)
        self.assertIn(f"/remove/{session.verify_token}/", body)
        self.assertNotIn("email", res.json())

    def test_rejects_non_glasgow_email(self):
        res = self.client.post("/api/sessions/", payload(email="me@gmail.com"), format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.json())

    def test_rejects_bad_duration(self):
        for bad in (15, 45, 400):
            res = self.client.post("/api/sessions/", payload(duration_minutes=bad), format="json")
            self.assertEqual(res.status_code, 400, bad)
            self.assertIn("duration_minutes", res.json())

    def test_rejects_level_outside_zone(self):
        res = self.client.post("/api/sessions/", payload(zone="silent", level=2), format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("level", res.json())

    def test_level_is_optional(self):
        res = self.client.post("/api/sessions/", payload(level=None), format="json")
        self.assertEqual(res.status_code, 201)

    def test_one_live_post_per_email(self):
        Session.objects.create(
            is_verified=True, start_time=timezone.now(), duration_minutes=60,
            **{k: v for k, v in payload().items() if k not in ("start_time", "duration_minutes")},
        )
        res = self.client.post("/api/sessions/", payload(), format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.json())


class BoardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        now = timezone.now()
        common = {k: v for k, v in payload().items() if k not in ("start_time", "duration_minutes")}
        self.live = Session.objects.create(is_verified=True, start_time=now, duration_minutes=60, **common)
        Session.objects.create(is_verified=False, start_time=now, duration_minutes=60, **common)
        Session.objects.create(
            is_verified=True, start_time=now - timedelta(hours=3), duration_minutes=60, **common
        )

    def test_list_only_shows_live_verified(self):
        res = self.client.get("/api/sessions/")
        self.assertEqual(res.status_code, 200)
        ids = [s["id"] for s in res.json()]
        self.assertEqual(ids, [self.live.id])

    def test_no_update_or_delete_via_api(self):
        url = f"/api/sessions/{self.live.id}/"
        self.assertEqual(self.client.delete(url).status_code, 405)
        self.assertEqual(self.client.patch(url, {"note": "x"}, format="json").status_code, 405)
        self.assertEqual(self.client.put(url, payload(), format="json").status_code, 405)


class TokenLinkTests(TestCase):
    def setUp(self):
        common = {k: v for k, v in payload().items() if k not in ("start_time", "duration_minutes")}
        self.session = Session.objects.create(start_time=timezone.now(), duration_minutes=60, **common)

    def test_verify_marks_live_and_redirects(self):
        res = self.client.get(reverse("verify", args=[self.session.verify_token]))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res["Location"].endswith(f"/?verified={self.session.id}"))
        self.session.refresh_from_db()
        self.assertTrue(self.session.is_verified)

    def test_verify_expired_post_does_not_go_live(self):
        self.session.start_time = timezone.now() - timedelta(hours=5)
        self.session.save()
        res = self.client.get(reverse("verify", args=[self.session.verify_token]))
        self.assertTrue(res["Location"].endswith("/?expired=1"))
        self.session.refresh_from_db()
        self.assertFalse(self.session.is_verified)

    def test_remove_deletes_and_redirects(self):
        res = self.client.get(reverse("remove", args=[self.session.verify_token]))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res["Location"].endswith("/?removed=1"))
        self.assertFalse(Session.objects.filter(pk=self.session.pk).exists())

    def test_unknown_token_404s(self):
        import uuid
        self.assertEqual(self.client.get(reverse("verify", args=[uuid.uuid4()])).status_code, 404)


class ResendBackendTests(TestCase):
    def test_posts_to_resend_api(self):
        import json
        from unittest import mock
        from django.core.mail import EmailMessage
        from board.email import ResendEmailBackend

        captured = {}

        class FakeResponse:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *a): return False

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            captured["auth"] = req.get_header("Authorization")
            captured["body"] = json.loads(req.data)
            return FakeResponse()

        with self.settings(RESEND_API_KEY="re_test", DEFAULT_FROM_EMAIL="Ascend <a@b.c>"):
            with mock.patch("urllib.request.urlopen", fake_urlopen):
                n = ResendEmailBackend().send_messages(
                    [EmailMessage("Subj", "Body", None, ["x@student.gla.ac.uk"])]
                )
        self.assertEqual(n, 1)
        self.assertEqual(captured["url"], "https://api.resend.com/emails")
        self.assertEqual(captured["auth"], "Bearer re_test")
        self.assertEqual(captured["body"]["to"], ["x@student.gla.ac.uk"])
        self.assertEqual(captured["body"]["subject"], "Subj")


class SpaRouteTests(TestCase):
    def test_spa_404s_when_not_built(self):
        from django.http import Http404
        from django.test import RequestFactory
        from config.urls import spa

        with self.settings(FRONTEND_DIST=settings.BASE_DIR / "nope"):
            with self.assertRaises(Http404):
                spa(RequestFactory().get("/"))

    def test_spa_serves_index_when_built(self):
        import tempfile
        from pathlib import Path
        from django.test import RequestFactory
        from config.urls import spa

        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "index.html").write_text("<!doctype html><title>Ascend</title>")
            with self.settings(FRONTEND_DIST=Path(d)):
                res = spa(RequestFactory().get("/anything"))
                self.assertEqual(res.status_code, 200)
                self.assertIn(b"Ascend", b"".join(res.streaming_content))

    def test_api_routes_untouched(self):
        self.assertEqual(self.client.get("/api/sessions/").status_code, 200)


class OwnerActionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        common = {k: v for k, v in payload().items() if k not in ("start_time", "duration_minutes")}
        self.s = Session.objects.create(
            is_verified=True, start_time=timezone.now(), duration_minutes=60, **common
        )
        self.key = str(self.s.verify_token)

    def test_create_returns_owner_key_once(self):
        res = self.client.post("/api/sessions/", payload(email="other1@student.gla.ac.uk"), format="json")
        self.assertEqual(res.status_code, 201)
        key = res.json()["owner_key"]
        self.assertEqual(key, str(Session.objects.get(pk=res.json()["id"]).verify_token))
        # Not exposed on the board.
        Session.objects.filter(pk=res.json()["id"]).update(is_verified=True)
        for row in self.client.get("/api/sessions/").json():
            self.assertNotIn("owner_key", row)
            self.assertNotIn("verify_token", row)

    def test_leave_requires_key(self):
        res = self.client.post(f"/api/sessions/{self.s.id}/leave/", {"owner_key": "nope"}, format="json")
        self.assertEqual(res.status_code, 403)
        self.assertTrue(Session.objects.filter(pk=self.s.pk).exists())

    def test_leave_deletes_with_key(self):
        res = self.client.post(f"/api/sessions/{self.s.id}/leave/", {"owner_key": self.key}, format="json")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Session.objects.filter(pk=self.s.pk).exists())

    def test_extend_adds_30_minutes(self):
        before = self.s.end_time
        res = self.client.post(f"/api/sessions/{self.s.id}/extend/", {"owner_key": self.key}, format="json")
        self.assertEqual(res.status_code, 200)
        self.s.refresh_from_db()
        self.assertEqual(self.s.end_time, before + timedelta(minutes=30))
        self.assertEqual(self.s.duration_minutes, 90)

    def test_extend_capped_at_six_hours(self):
        self.s.duration_minutes = 360
        self.s.save()
        res = self.client.post(f"/api/sessions/{self.s.id}/extend/", {"owner_key": self.key}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_extend_wrong_key(self):
        res = self.client.post(f"/api/sessions/{self.s.id}/extend/", {"owner_key": "x"}, format="json")
        self.assertEqual(res.status_code, 403)


class AdminStatsTests(TestCase):
    def test_stats_page_renders_for_staff(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser("admin", "a@b.c", "pw")
        self.client.login(username="admin", password="pw")
        common = {k: v for k, v in payload().items() if k not in ("start_time", "duration_minutes")}
        Session.objects.create(is_verified=True, start_time=timezone.now(), duration_minutes=60, **common)
        res = self.client.get("/admin/board/session/stats/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "verify rate")
        self.assertContains(res, "Group study")

    def test_stats_requires_login(self):
        res = self.client.get("/admin/board/session/stats/")
        self.assertEqual(res.status_code, 302)
