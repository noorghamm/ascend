from django.utils import timezone
from rest_framework import serializers

from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Session
        fields = [
            "id", "email", "display_name", "zone", "level",
            "start_time", "duration_minutes", "end_time",
            "note", "contact", "created_at",
        ]
        read_only_fields = ["id", "end_time", "created_at"]

    def validate_email(self, value):
        value = value.lower().strip()
        if not value.endswith("@student.gla.ac.uk"):
            raise serializers.ValidationError(
                "Use your University of Glasgow student email."
            )
        return value

    def validate_display_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value

    def validate_duration_minutes(self, value):
        if value < 30 or value > 360 or value % 30 != 0:
            raise serializers.ValidationError(
                "Duration must be between 30 minutes and 6 hours, in half-hour steps."
            )
        return value

    def validate(self, attrs):
        zone = attrs.get("zone")
        level = attrs.get("level")
        if level is not None and level not in Session.ZONE_LEVELS.get(zone, []):
            allowed = ", ".join(str(l) for l in Session.ZONE_LEVELS.get(zone, []))
            raise serializers.ValidationError(
                {"level": f"That level isn't in this zone. Try: {allowed}."}
            )

        # One live post per email: either already on the board, or verified-pending
        # and created in the last 15 minutes (so a typo'd post can be retried soon).
        email = attrs.get("email")
        if email and self.instance is None:
            now = timezone.now()
            live = Session.objects.filter(
                email=email, is_verified=True, end_time__gt=now
            ).exists()
            if live:
                raise serializers.ValidationError(
                    {"email": "You already have a live post. Remove it first via the link in your email."}
                )
        return attrs
