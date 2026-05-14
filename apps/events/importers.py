import json
from dataclasses import dataclass, field

from django.db import transaction
from django.utils.dateparse import parse_datetime

from .models import Event


class EventImportError(Exception):
    pass


@dataclass
class EventImportResult:
    created_count: int = 0
    updated_count: int = 0
    deleted_count: int = 0
    skipped_count: int = 0
    event_count: int = 0
    errors: list = field(default_factory=list)


def _load_json(uploaded_file):
    try:
        raw = uploaded_file.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        payload = json.loads(raw)
    except UnicodeDecodeError as exc:
        raise EventImportError("The uploaded file must be UTF-8 encoded JSON.") from exc
    except json.JSONDecodeError as exc:
        raise EventImportError(f"Invalid JSON: {exc.msg}") from exc

    if not isinstance(payload, list):
        raise EventImportError("The root JSON value must be a list of event objects.")

    return payload


def _normalize_event_type(raw):
    allowed = {choice[0] for choice in Event.EVENT_TYPE_CHOICES}
    value = (raw or "").strip().lower()
    if value not in allowed:
        raise EventImportError(
            f"Unsupported event_type '{raw}'. Allowed: {', '.join(sorted(allowed))}."
        )
    return value


def _normalize_priority(raw):
    if not raw:
        return None
    allowed = {choice[0] for choice in Event.PRIORITY_CHOICES}
    value = raw.strip().lower()
    if value not in allowed:
        raise EventImportError(
            f"Unsupported priority '{raw}'. Allowed: {', '.join(sorted(allowed))}."
        )
    return value


def _normalize_status(raw):
    if not raw:
        return "pending"
    allowed = {choice[0] for choice in Event.STATUS_CHOICES}
    value = raw.strip().lower()
    if value not in allowed:
        raise EventImportError(
            f"Unsupported status '{raw}'. Allowed: {', '.join(sorted(allowed))}."
        )
    return value


def _normalize_recurrence(raw):
    if not raw:
        return "none"
    allowed = {choice[0] for choice in Event.RECURRENCE_CHOICES}
    value = raw.strip().lower()
    if value not in allowed:
        raise EventImportError(
            f"Unsupported recurrence '{raw}'. Allowed: {', '.join(sorted(allowed))}."
        )
    return value


def _parse_event(item, index):
    if not isinstance(item, dict):
        raise EventImportError(f"Event #{index + 1} must be a JSON object.")

    title = (item.get("title") or "").strip()
    if not title:
        raise EventImportError(f"Event #{index + 1} is missing a 'title'.")

    start_datetime = parse_datetime(item.get("start_datetime") or "")
    if not start_datetime:
        raise EventImportError(
            f"Event #{index + 1} ('{title}') must contain a valid 'start_datetime' (ISO 8601)."
        )

    end_raw = item.get("end_datetime")
    end_datetime = parse_datetime(end_raw) if end_raw else None
    if end_raw and not end_datetime:
        raise EventImportError(
            f"Event #{index + 1} ('{title}') has an invalid 'end_datetime' format."
        )

    if end_datetime and end_datetime <= start_datetime:
        raise EventImportError(
            f"Event #{index + 1} ('{title}'): 'end_datetime' must be after 'start_datetime'."
        )

    return {
        "title": title,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "event_type": _normalize_event_type(item.get("event_type")),
        "priority": _normalize_priority(item.get("priority")),
        "status": _normalize_status(item.get("status")),
        "recurrence": _normalize_recurrence(item.get("recurrence")),
        "location": (item.get("location") or "").strip(),
        "expected_attendees": item.get("expected_attendees") or None,
        "description": (item.get("description") or "").strip(),
    }


def _upsert_event(payload):
    existing = Event.objects.filter(
        title=payload["title"],
        start_datetime=payload["start_datetime"],
    ).first()

    if existing is None:
        Event.objects.create(**payload)
        return "created"

    # Update only dirty fields
    dirty_fields = []
    for key, value in payload.items():
        if getattr(existing, key) != value:
            setattr(existing, key, value)
            dirty_fields.append(key)

    if dirty_fields:
        existing.save(update_fields=dirty_fields)
        return "updated"

    return "skipped"


@transaction.atomic
def import_events_json(uploaded_file, replace_existing=False):
    payload = _load_json(uploaded_file)
    result = EventImportResult(event_count=len(payload))

    # Parse all first — fail fast before any DB writes
    parsed_events = []
    for index, item in enumerate(payload):
        try:
            parsed_events.append(_parse_event(item, index))
        except EventImportError as exc:
            result.errors.append(str(exc))

    if result.errors:
        raise EventImportError(
            f"Found {len(result.errors)} error(s) in JSON:\n"
            + "\n".join(f"  • {e}" for e in result.errors)
        )

    # Optional: delete existing events on matching dates before import
    if replace_existing and parsed_events:
        dates = {e["start_datetime"].date() for e in parsed_events}
        delete_qs = Event.objects.filter(start_datetime__date__in=dates)
        result.deleted_count = delete_qs.count()
        delete_qs.delete()

    # Upsert each event
    for event_payload in parsed_events:
        outcome = _upsert_event(event_payload)
        if outcome == "created":
            result.created_count += 1
        elif outcome == "updated":
            result.updated_count += 1
        else:
            result.skipped_count += 1

    return result
