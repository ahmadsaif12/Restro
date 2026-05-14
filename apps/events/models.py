from django.db import models
from django.conf import settings
from apps.misc.models import BaseModel


class Event(BaseModel):
    EVENT_TYPE_CHOICES = [
        ("meeting", "Meeting"),
        ("reservation", "Reservation"),
        ("task", "Task"),
        ("training", "Training"),
        ("other", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    RECURRENCE_CHOICES = [
        ("none", "None"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    title = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    expected_attendees = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    recurrence = models.CharField(
        max_length=20, choices=RECURRENCE_CHOICES, default="none"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["start_datetime"]

    def __str__(self):
        return f"{self.title} - {self.start_datetime.date()}"
