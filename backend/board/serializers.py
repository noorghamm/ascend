from rest_framework import serializers
from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    end_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Session
        fields = [
            "id", "display_name", "zone", "level",
            "start_time", "duration_minutes", "end_time",
            "note", "contact", "created_at",
        ]
        read_only_fields = ["id", "created_at"]