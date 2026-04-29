from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    inline_serializer,
    OpenApiResponse
)

from .models import InventoryItem
from .serializers import InventoryItemSerializer


def not_found():
    return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class InventoryDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Inventory dashboard summary cards",
        responses=inline_serializer(
            name="InventoryDashboardResponse",
            fields={
                "total_items": serializers.IntegerField(),
                "low_stock_alerts": serializers.IntegerField(),
                "total_inventory_value": serializers.FloatField(),
            }
        )
    )
    def get(self, request):
        items = InventoryItem.objects.all()
        total_value = items.aggregate(
            total=Sum(F("current_stock") * F("unit_cost"))
        )["total"] or 0

        return Response({
            "total_items": items.count(),
            "low_stock_alerts": sum(1 for i in items if i.is_low_stock),
            "total_inventory_value": round(total_value, 2),
        })


class InventoryItemView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all inventory items",
        parameters=[
            OpenApiParameter(
                "search", str,
                description="Search by name or supplier"
            ),
            OpenApiParameter(
                "unit", str,
                description="Filter by unit",
                enum=["kg", "g", "l", "ml", "pcs", "dozen", "box"]
            ),
        ],
        responses=InventoryItemSerializer(many=True)
    )
    def get(self, request):
        qs = InventoryItem.objects.select_related("category").all()
        search = request.query_params.get("search")
        unit = request.query_params.get("unit")

        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(supplier__icontains=search)

        if unit:
            qs = qs.filter(unit=unit)

        return Response(InventoryItemSerializer(qs, many=True).data)

    @extend_schema(
        summary="Add new inventory item",
        request=inline_serializer(
            name="InventoryItemCreateRequest",
            fields={
                "name": serializers.CharField(),
                "category": serializers.CharField(help_text="e.g. Meat, Dairy, Vegetables"),
                "unit": serializers.ChoiceField(choices=["kg", "g", "l", "ml", "pcs", "dozen", "box"]),
                "current_stock": serializers.DecimalField(max_digits=10, decimal_places=3),
                "min_stock": serializers.DecimalField(max_digits=10, decimal_places=3),
                "unit_cost": serializers.DecimalField(max_digits=10, decimal_places=2),
                "supplier": serializers.CharField(required=False, allow_blank=True),
            }
        ),
        responses=InventoryItemSerializer
    )
    def post(self, request):
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return InventoryItem.objects.select_related("category").get(pk=pk)
        except InventoryItem.DoesNotExist:
            return None

    @extend_schema(
        summary="Update inventory item",
        request=inline_serializer(
            name="InventoryItemUpdateRequest",
            fields={
                "name": serializers.CharField(required=False),
                "category": serializers.CharField(required=False),
                "unit": serializers.ChoiceField(
                    choices=["kg", "g", "l", "ml", "pcs", "dozen", "box"],
                    required=False
                ),
                "current_stock": serializers.DecimalField(max_digits=10, decimal_places=3, required=False),
                "min_stock": serializers.DecimalField(max_digits=10, decimal_places=3, required=False),
                "unit_cost": serializers.DecimalField(max_digits=10, decimal_places=2, required=False),
                "supplier": serializers.CharField(required=False, allow_blank=True),
            }
        ),
        responses=InventoryItemSerializer
    )
    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return not_found()

        serializer = InventoryItemSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete inventory item",
        responses={
            204: OpenApiResponse(description="No Content")
        }
    )
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return not_found()

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)