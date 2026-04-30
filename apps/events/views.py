from rest_framework import viewsets, permissions
from django.utils import timezone
from apps.events.models import Event
from apps.events.serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Event.objects.all().order_by("date", "time")
        filter_type = self.request.query_params.get("filter", "all")
        today = timezone.localdate()

        if filter_type == "today":
            queryset = queryset.filter(date=today)
        elif filter_type == "upcoming":
            queryset = queryset.filter(date__gt=today)

        return queryset

    def perform_create(self, serializer):
        serializer.save()