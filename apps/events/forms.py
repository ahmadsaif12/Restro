from django import forms


class CalendarImportForm(forms.Form):
    json_file = forms.FileField(
        label="Calendar JSON File",
        help_text="Upload a JSON file containing event details. See expected format below.",
    )
    replace_existing = forms.BooleanField(
        required=False,
        label="Replace existing events on imported dates",
        help_text="If enabled, existing events matching the same start date are removed before import.",
    )
