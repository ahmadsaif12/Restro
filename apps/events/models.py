from django.db import models

class Events(models.Model):

    EVENT_TYPE_CHOICES = [
        ("meeting", "Meeting"),
        ("event", "Event"),
        ("task", "Task"),
        ("reservation", "Reservation"),
    ]

    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    location = models.CharField(max_length=255, blank=True, null=True)
    attendees = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title