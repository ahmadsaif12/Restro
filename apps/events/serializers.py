from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        if not data.get("title"):
            raise serializers.ValidationError({"title": "Event title is required."})
        if not data.get("date"):
            raise serializers.ValidationError({"date": "Date is required."})
        if not data.get("time"):
            raise serializers.ValidationError({"time": "Time is required."})
        if not data.get("event_type"):
            raise serializers.ValidationError({"event_type": "Event type is required."})
        if not data.get("location"):
            raise serializers.ValidationError({"location": "Location is required."})
        return data


class EventSummarySerializer(serializers.Serializer):
    """For the dashboard stats (Total Events, Expected Guests)"""

    total_events = serializers.IntegerField()
    total_expected_guests = serializers.IntegerField()
