from django.db import models
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

    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True
    )
    location = models.CharField(max_length=255)
    expected_attendees = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.title} - {self.date}"
