from django.urls import path
from .views import (
    InventoryDashboardView,
    InventoryItemView,
    InventoryItemDetailView,
    InventoryCategoryListView,
    InventoryCategoryDetailView,
)

urlpatterns = [
    path("dashboard-inventory/", InventoryDashboardView.as_view(), name="inventory-dashboard"),
    path("categories/", InventoryCategoryListView.as_view(), name="inventory-category-list"),
    path("categories/<slug:slug>/", InventoryCategoryDetailView.as_view(), name="inventory-category-detail"),
    path("items/", InventoryItemView.as_view(), name="item-list"),
    path("items/<int:pk>/", InventoryItemDetailView.as_view(), name="item-detail"),
]