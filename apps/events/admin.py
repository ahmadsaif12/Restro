from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date",
        "time",
        "event_type",
        "priority",
        "location",
        "created_at",
    )
    list_filter = (
        "event_type",
        "priority",
        "date",
    )
    search_fields = (
        "title",
        "location",
        "attendees",
        "description",
    )
    ordering = ("-date", "-time")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "event_type", "priority")
        }),
        ("Schedule", {
            "fields": ("date", "time")
        }),
        ("Details", {
            "fields": ("location", "attendees", "description")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )