from django.urls import path
from .views import (
    DashboardAPIView,
    VendorDetailAPIView,
    VendorListAPIView,
    RecordPurchaseAPIView,
    MarkPaidAPIView,
)

urlspatterns = [
    path("api/dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("api/vendors/", VendorListAPIView.as_view(), name="vendor-list"),
    path("api/vendors/<int:pk>/", VendorDetailAPIView.as_view(), name="vendor-detail"),
    path("api/purchases/", RecordPurchaseAPIView.as_view(), name="record-purchase"),
    path(
        "api/purchases/<int:pk>/mark-paid/", MarkPaidAPIView.as_view(), name="mark-paid"
    ),
]
