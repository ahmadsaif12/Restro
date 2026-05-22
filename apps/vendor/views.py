from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer

from .models import Vendor, Purchase
from .serializers import (
    RecordPurchaseSerializer,
    VendorDetailSerializer,
    VendorListSerializer,
    DashboardSerializer,
)


class DashboardAPIView(APIView):
    @extend_schema(
        summary="Dashboard Stats",
        responses={200: DashboardSerializer},
        tags=["Dashboard"],
    )
    def get(self, request):
        vendors = Vendor.objects.all()
        total_pending = sum(v.total_pending for v in vendors)
        vendors_with_pending = sum(1 for v in vendors if v.total_pending > 0)
        total_vendors = vendors.count()

        data = {
            "total_pending": total_pending,
            "vendors_with_pending": vendors_with_pending,
            "total_vendors": total_vendors,
        }
        return Response(DashboardSerializer(data).data)


class VendorListAPIView(APIView):
    @extend_schema(
        summary="Vendor List",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Name,email and phone",
                required=False,
                type=str,
            )
        ],
        responses={200: VendorListSerializer(many=True)},
        tags=["Vendors"],
    )
    def get(self, request):
        search = request.query_params.get("search", "").strip()
        vendors = Vendor.objects.all()

        if search:
            vendors = vendors.filter(
                Q(vendor_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )

        return Response(VendorListSerializer(vendors, many=True).data)


class VendorDetailAPIView(APIView):
    @extend_schema(
        summary="Vendor Detail",
        responses={
            200: VendorDetailSerializer,
            404: inline_serializer(
                name="VendorNotFound",
                fields={"error": serializers.CharField()},
            ),
        },
        tags=["Vendors"],
    )
    def get(self, request, pk):
        try:
            vendor = Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor fela parena."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(VendorDetailSerializer(vendor).data)


class RecordPurchaseAPIView(APIView):
    @extend_schema(
        summary="Record New Purchase",
        request=RecordPurchaseSerializer,
        responses={
            201: inline_serializer(
                name="PurchaseCreated",
                fields={
                    "message": serializers.CharField(),
                    "id": serializers.IntegerField(),
                },
            ),
            400: inline_serializer(
                name="PurchaseValidationError",
                fields={"vendor_name": serializers.ListField()},
            ),
        },
        tags=["Purchases"],
    )
    def post(self, request):
        serializer = RecordPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            purchase = serializer.save()
            return Response(
                {"message": "Purchase record bhayo!", "id": purchase.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkPaidAPIView(APIView):
    @extend_schema(
        summary="Mark Purchase as Paid",
        request=None,
        responses={
            200: inline_serializer(
                name="MarkPaidResponse",
                fields={"message": serializers.CharField()},
            ),
            404: inline_serializer(
                name="PurchaseNotFound",
                fields={"error": serializers.CharField()},
            ),
        },
        tags=["Purchases"],
    )
    def patch(self, request, pk):
        try:
            purchase = Purchase.objects.get(pk=pk)
        except Purchase.DoesNotExist:
            return Response(
                {"error": "Purchase fela parena."},
                status=status.HTTP_404_NOT_FOUND,
            )

        purchase.is_paid = True
        purchase.save()
        return Response({"message": "Purchase paid completed"})
