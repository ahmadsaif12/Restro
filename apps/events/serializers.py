from rest_framework import serializers
from django.utils import timezone
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        # Required field checks (title & event_type are already handled
        # by model, but explicit messages are friendlier)
        if not data.get("title"):
            raise serializers.ValidationError({"title": "Event title is required."})

        if not data.get("start_datetime"):
            raise serializers.ValidationError(
                {"start_datetime": "Start datetime is required."}
            )

        if not data.get("event_type"):
            raise serializers.ValidationError({"event_type": "Event type is required."})

        start = data.get("start_datetime")
        end = data.get("end_datetime")
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_datetime": "End datetime must be after start datetime."}
            )

        # Prevent creating events in the past (only on create, not on update)
        if self.instance is None and start and start < timezone.now():
            raise serializers.ValidationError(
                {"start_datetime": "Cannot create an event in the past."}
            )

        return data


class EventSummarySerializer(serializers.Serializer):
    """For the dashboard stats (Total Events, Expected Guests)"""

    total_events = serializers.IntegerField()
    total_expected_guests = serializers.IntegerField()
