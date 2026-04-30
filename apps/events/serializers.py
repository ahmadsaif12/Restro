from rest_framework import serializers
from django.utils import timezone
from apps.events.models import Event
from drf_spectacular.utils import extend_schema_field

class EventSerializer(serializers.ModelSerializer):
    local_date = serializers.SerializerMethodField()
    local_time = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'local_date', 'local_time']

    @extend_schema_field(serializers.CharField()) 
    def get_local_date(self, obj):
        return obj.date 
        
    @extend_schema_field(serializers.CharField()) 
    def get_local_time(self, obj):
        return obj.time