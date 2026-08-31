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
        if not value.lower().endswith("@student.gla.ac.uk"):
            raise serializers.ValidationError(
                "Use your University of Glasgow student email."
            )
        return value
    
    def validate_duration_minutes(self, value):
        if value < 30 or value > 360 or value % 30 != 0:
            raise serializers.ValidationError(
                "Duration must be between 30 minutes and 6 hours, in half-hour steps."
            )
        return value

      