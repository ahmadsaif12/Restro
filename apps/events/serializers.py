from rest_framework import serializers
from django.utils import timezone
from apps.events.models import Events

class EventSerializer(serializers.ModelSerializer):
    local_date = serializers.SerializerMethodField()
    local_time = serializers.SerializerMethodField()

    class Meta:
        model = Events
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'local_date', 'local_time']

    def get_local_date(self, obj):
        return obj.date 

    def get_local_time(self, obj):
        return obj.time