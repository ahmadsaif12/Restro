from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Event
from .forms import CalendarImportForm
import json


class MonthFilter(admin.SimpleListFilter):
    title = "Month"
    parameter_name = "month"

    MONTHS = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    def lookups(self, request, model_admin):
        return [(str(n), label) for n, label in self.MONTHS]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(start_datetime__month=self.value())
        return queryset


class YearFilter(admin.SimpleListFilter):
    title = "Year"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        years = (
            model_admin.get_queryset(request)
            .values_list("start_datetime__year", flat=True)
            .distinct()
            .order_by("start_datetime__year")
        )
        return [(str(y), str(y)) for y in years if y]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(start_datetime__year=self.value())
        return queryset


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    change_list_template = "admin/events/change_list.html"

    list_display = (
        "title",
        "display_event_type",
        "display_priority",
        "display_status",
        "start_datetime",
        "end_datetime",
        "location",
        "expected_attendees",
        "created_at",
    )
    list_filter = (
        "event_type",
        "priority",
        "status",
        "recurrence",
        YearFilter,
        MonthFilter,
    )
    search_fields = ("title", "location", "description")
    search_help_text = "Search by title, location, or description."
    ordering = ("-start_datetime",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_datetime"
    list_per_page = 50

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("title", "event_type", "priority", "status"),
            },
        ),
        (
            "Schedule",
            {
                "fields": ("start_datetime", "end_datetime", "recurrence"),
            },
        ),
        (
            "Details",
            {
                "fields": ("location", "expected_attendees", "description"),
            },
        ),
        (
            "Meta",
            {
                "fields": ("created_by", "created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("created_by")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-json/",
                self.admin_site.admin_view(self.import_json_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_import_json",
            )
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        extra_context["event_stats"] = {
            "total_events": qs.count(),
            "confirmed_events": qs.filter(status="confirmed").count(),
            "pending_events": qs.filter(status="pending").count(),
            "cancelled_events": qs.filter(status="cancelled").count(),
        }
        extra_context["import_url"] = self._import_url()
        return super().changelist_view(request, extra_context=extra_context)

    def import_json_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        form = CalendarImportForm(request.POST or None, request.FILES or None)

        if request.method == "POST" and form.is_valid():
            try:
                created, skipped = self._process_import(
                    file=form.cleaned_data["json_file"],
                    replace_existing=form.cleaned_data["replace_existing"],
                )
            except Exception as exc:
                form.add_error("json_file", f"Import failed: {exc}")
            else:
                self.message_user(
                    request,
                    f"Import complete — {created} created, {skipped} skipped.",
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect(self._changelist_url())

        # Compute event statistics for display in the import template
        qs = self.get_queryset(request)
        event_stats = {
            "total_events": qs.count(),
            "confirmed_events": qs.filter(status="confirmed").count(),
            "pending_events": qs.filter(status="pending").count(),
            "cancelled_events": qs.filter(status="cancelled").count(),
        }
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Import Events from JSON",
            "form": form,
            "has_view_permission": self.has_view_permission(request),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_change_permission(request),
            "has_delete_permission": self.has_delete_permission(request),
            "import_url": self._import_url(),
            "changelist_url": self._changelist_url(),
            "event_stats": event_stats,
        }
        return TemplateResponse(request, "admin/events/import_form.html", context)

    def _process_import(self, file, replace_existing):
        data = json.loads(file.read())
        created = skipped = 0

        for item in data:
            start = item.get("start_datetime")

            if replace_existing and start:
                Event.objects.filter(start_datetime__date=start[:10]).delete()

            _, was_created = Event.objects.get_or_create(
                title=item["title"],
                start_datetime=item["start_datetime"],
                defaults={
                    "end_datetime": item.get("end_datetime"),
                    "event_type": item.get("event_type", "other"),
                    "priority": item.get("priority"),
                    "location": item.get("location", ""),
                    "expected_attendees": item.get("expected_attendees"),
                    "description": item.get("description", ""),
                    "status": item.get("status", "pending"),
                    "recurrence": item.get("recurrence", "none"),
                },
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        return created, skipped

    def _changelist_url(self):
        return reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
        )

    def _import_url(self):
        return reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_import_json"
        )

    def display_event_type(self, obj):
        palette = {
            "meeting": "#1d4ed8",
            "reservation": "#0369a1",
            "task": "#475569",
            "training": "#b45309",
            "other": "#64748b",
        }
        color = palette.get(obj.event_type, "#475569")
        return format_html(
            '<span style="display:inline-block;padding:0.25rem 0.65rem;border-radius:999px;'
            'background:{}18;color:{};font-weight:600;text-transform:capitalize;">{}</span>',
            color,
            color,
            obj.get_event_type_display(),
        )

    display_event_type.short_description = "Type"
    display_event_type.admin_order_field = "event_type"

    def display_priority(self, obj):
        if not obj.priority:
            return "—"
        palette = {
            "low": "#16a34a",
            "medium": "#d97706",
            "high": "#dc2626",
        }
        color = palette.get(obj.priority, "#475569")
        return format_html(
            '<span style="display:inline-block;padding:0.25rem 0.65rem;border-radius:999px;'
            'background:{}18;color:{};font-weight:600;text-transform:capitalize;">{}</span>',
            color,
            color,
            obj.get_priority_display(),
        )

    display_priority.short_description = "Priority"
    display_priority.admin_order_field = "priority"

    def display_status(self, obj):
        palette = {
            "pending": "#d97706",
            "confirmed": "#16a34a",
            "cancelled": "#dc2626",
            "completed": "#475569",
        }
        color = palette.get(obj.status, "#475569")
        return format_html(
            '<span style="display:inline-block;padding:0.25rem 0.65rem;border-radius:999px;'
            'background:{}18;color:{};font-weight:600;text-transform:capitalize;">{}</span>',
            color,
            color,
            obj.get_status_display(),
        )

    display_status.short_description = "Status"
    display_status.admin_order_field = "status"
