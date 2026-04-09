from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "handle_my_restore.settings")

app = Celery("handle_my_restore")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

