# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from .models import Event
from .serializers import EventSerializer, EventSummarySerializer


@extend_schema_view(
    list=extend_schema(
        description="Returns a list of all calendar events. Supports filtering by `filter` and `date` query params.",
        parameters=[
            OpenApiParameter(
                name="filter",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter events: `all`, `today`, or `upcoming`",
                enum=["all", "today", "upcoming"],
                required=False,
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter events by specific date (YYYY-MM-DD)",
                required=False,
            ),
        ],
        responses={200: EventSerializer(many=True)},
    ),
    create=extend_schema(
        description="Creates a new calendar event with the provided details.",
        request=EventSerializer,
        responses={
            201: EventSerializer,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="Staff Training Example",
                value={
                    "title": "Staff Training",
                    "start_datetime": "2026-05-14T15:00:00",
                    "end_datetime": "2026-05-14T17:00:00",
                    "event_type": "meeting",
                    "priority": "medium",
                    "location": "Training Room",
                    "expected_attendees": 12,
                    "description": "Customer service excellence training",
                    "status": "pending",
                },
                request_only=True,
            )
        ],
    ),
    partial_update=extend_schema(
        description="Partially updates a calendar event by ID (e.g. status change).",
        request=EventSerializer,
        responses={
            200: EventSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    destroy=extend_schema(
        description="Deletes a calendar event by ID.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = Event.objects.all()
        filter_type = self.request.query_params.get("filter")
        date_param = self.request.query_params.get("date")
        today = timezone.now().date()

        if filter_type == "today":
            queryset = queryset.filter(start_datetime__date=today)
        elif filter_type == "upcoming":
            queryset = queryset.filter(start_datetime__date__gte=today)
        if date_param:
            queryset = queryset.filter(start_datetime__date=date_param)

        return queryset

    @extend_schema(
        description="Returns total number of events and total expected guests for the dashboard header.",
        responses={200: EventSummarySerializer},
    )
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        total_events = Event.objects.count()
        total_guests = (
            Event.objects.aggregate(total=Sum("expected_attendees"))["total"] or 0
        )
        data = {
            "total_events": total_events,
            "total_expected_guests": total_guests,
        }
        serializer = EventSummarySerializer(data)
        return Response(serializer.data)

    @extend_schema(
        description="Returns all events scheduled for a specific date.",
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="The date to fetch events for (YYYY-MM-DD)",
                required=True,
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "date": "2026-05-14",
                    "count": 1,
                    "events": [
                        {
                            "id": 1,
                            "title": "Staff Training",
                            "start_datetime": "2026-05-14T15:00:00",
                            "end_datetime": "2026-05-14T17:00:00",
                            "event_type": "meeting",
                            "priority": "medium",
                            "location": "Training Room",
                            "expected_attendees": 12,
                            "description": "Customer service excellence training",
                            "status": "pending",
                        }
                    ],
                },
                response_only=True,
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="by-date")
    def by_date(self, request):
        date_param = request.query_params.get("date")
        if not date_param:
            return Response(
                {"error": "date query param required (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        events = Event.objects.filter(start_datetime__date=date_param)
        serializer = self.get_serializer(events, many=True)
        return Response(
            {"date": date_param, "count": events.count(), "events": serializer.data}
        )
