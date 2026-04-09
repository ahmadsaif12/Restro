from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.events.views import EventViewSet

router = SimpleRouter()
router.register(r'', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]