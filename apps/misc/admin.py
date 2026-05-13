from django.contrib import admin
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    SolarSchedule,
    PeriodicTask,
)
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from django.contrib.auth.models import Group

# Unregister Group model
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Unregister models from django_celery_beat
models_to_unregister = [
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    SolarSchedule,
    PeriodicTask,
]

for model in models_to_unregister:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Unregister models from rest_framework_simplejwt.token_blacklist
jwt_models = [BlacklistedToken, OutstandingToken]
for model in jwt_models:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Unregister models from django_celery_results
try:
    from django_celery_results.models import TaskResult, GroupResult

    results_models = [TaskResult, GroupResult]
    for model in results_models:
        try:
            admin.site.unregister(model)
        except admin.sites.NotRegistered:
            pass
except ImportError:
    pass
