from rest_framework import serializers
from django.utils import timezone
from apps.events.models import Events

class EventSerializer(serializers.ModelSerializer):
    local_date = serializers.SerializerMethodField()
    local_time = serializers.SerializerMethodField()

    class Meta:
        model = Events
        fields = "__all__"

    def get_local_date(self, obj):
        if obj.date:
            return timezone.localtime(timezone.make_aware(timezone.datetime.combine(obj.date, timezone.datetime.min.time()))).date()
        return None

    def get_local_time(self, obj):
        if obj.time:
            return obj.time  
        return None