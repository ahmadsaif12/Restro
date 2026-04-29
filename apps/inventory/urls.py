from django.urls import path
from .views import (
    InventoryDashboardView,
    InventoryItemView,
    InventoryItemDetailView,
)

urlpatterns = [
    path("dashboard-inventory/", InventoryDashboardView.as_view(),  name="inventory-dashboard"),
    path("items/",               InventoryItemView.as_view(),       name="item-list"),
    path("items/<int:pk>/",      InventoryItemDetailView.as_view(), name="item-detail"),
]