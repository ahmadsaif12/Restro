from __future__ import annotations
import base64, json

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    inline_serializer,
)
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .payment_strategies import get_payment_strategy
from .utils import verify_esewa_signature

ALLOWED_UPDATE_FIELDS = {"order_status", "payment_status", "table", "notes"}


@extend_schema_view(
    list=extend_schema(
        summary="List orders",
        parameters=[
            OpenApiParameter("order_status", str),
            OpenApiParameter("payment_status", str),
            OpenApiParameter("payment_method", str),
            OpenApiParameter("search", str),
            OpenApiParameter("ordering", str),
        ],
    ),
    retrieve=extend_schema(summary="Retrieve order"),
    destroy=extend_schema(summary="Delete order"),
)
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["order_status", "payment_status", "payment_method"]
    search_fields = ["order_code", "user__username", "user__email"]
    ordering_fields = ["created_at", "total_amount"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Order.objects.select_related("user", "table")
            .prefetch_related("items__menu_item")
            .order_by("-created_at")
        )
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs

    @extend_schema(
        summary="Create order",
        request=OrderSerializer,
        responses={201: OrderSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)
        order.recalculate_total()
        payment_data = self._get_payment_payload(order)
        if isinstance(payment_data, Response):
            return payment_data
        return Response(
            {
                "message": "Order created.",
                "order": OrderSerializer(order).data,
                **payment_data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Update order (allowed: order_status, payment_status, table, notes)",
        request=inline_serializer(
            "OrderPutRequest",
            fields={
                "order_status": serializers.CharField(required=False),
                "payment_status": serializers.CharField(required=False),
                "table": serializers.IntegerField(required=False),
                "notes": serializers.CharField(required=False),
            },
        ),
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="No valid fields"),
        },
    )
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        filtered_data = {
            k: v for k, v in request.data.items() if k in ALLOWED_UPDATE_FIELDS
        }
        if not filtered_data:
            return Response(
                {
                    "error": f"No valid fields provided. Allowed: {sorted(ALLOWED_UPDATE_FIELDS)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = OrderSerializer(
            order, data=filtered_data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Order updated.", "order": serializer.data})

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        summary="Print KOT — returns pending items and marks them as Sent",
        responses={
            200: OpenApiResponse(description="KOT data with pending items"),
            400: OpenApiResponse(description="No pending items"),
        },
    )
    @action(detail=True, methods=["post"], url_path="print_kot")
    def print_kot(self, request, pk=None):
        order = self.get_object()
        pending_items = order.items.filter(kot_status="Pending")

        if not pending_items.exists():
            return Response(
                {"error": "No pending items to print KOT for."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Snapshot items before marking them sent
        kot_items = OrderItemSerializer(pending_items, many=True).data

        # Mark as Sent so they don't appear on next KOT print
        pending_items.update(kot_status="Sent")

        # Move order to In Progress if it's still New
        if order.order_status == "New":
            order.order_status = "In Progress"
            order.save(update_fields=["order_status"])

        return Response(
            {
                "message": "KOT printed successfully.",
                "order_code": f"ORD-{order.order_code}",
                "table": str(order.table),
                "waiter": order.user.get_full_name() or order.user.username
                if order.user
                else "—",
                "kot_items": kot_items,
                "total_items": sum(item["quantity"] for item in kot_items),
            }
        )

    @extend_schema(
        summary="Get KOT preview — returns pending items without changing status",
        responses={200: OpenApiResponse(description="Pending KOT items")},
    )
    @action(detail=True, methods=["get"], url_path="kot_preview")
    def kot_preview(self, request, pk=None):
        order = self.get_object()
        pending_items = order.items.filter(kot_status="Pending")
        return Response(
            {
                "order_code": f"ORD-{order.order_code}",
                "table": str(order.table),
                "waiter": order.user.get_full_name() or order.user.username
                if order.user
                else "—",
                "pending_items": OrderItemSerializer(pending_items, many=True).data,
                "total_pending": pending_items.count(),
            }
        )

    @extend_schema(
        summary="Mark items as Prepared — kitchen marks sent items as done",
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="No sent items to prepare"),
        },
    )
    @action(detail=True, methods=["post"], url_path="mark_prepared")
    def mark_prepared(self, request, pk=None):
        order = self.get_object()
        sent_items = order.items.filter(kot_status="Sent")

        if not sent_items.exists():
            return Response(
                {"error": "No sent items to mark as prepared."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sent_items.update(kot_status="Prepared")

        # Auto-update order status to Ready if all items are prepared
        if not order.items.filter(kot_status__in=["Pending", "Sent"]).exists():
            order.order_status = "Ready"
            order.save(update_fields=["order_status"])

        return Response(
            {
                "message": "Items marked as prepared.",
                "order": OrderSerializer(order).data,
            }
        )

    @extend_schema(
        summary="Update a single order item's kot_status",
        request=inline_serializer(
            "KotStatusRequest",
            fields={
                "kot_status": serializers.ChoiceField(
                    choices=["Pending", "Sent", "Prepared"]
                ),
            },
        ),
        responses={
            200: OpenApiResponse(description="Item updated"),
            404: OpenApiResponse(description="Item not found"),
        },
    )
    @action(
        detail=True, methods=["patch"], url_path="items/(?P<item_id>[^/.]+)/kot_status"
    )
    def update_item_kot_status(self, request, pk=None, item_id=None):
        order = self.get_object()
        item = get_object_or_404(OrderItem, pk=item_id, order=order)
        new_status = request.data.get("kot_status")
        if new_status not in ["Pending", "Sent", "Prepared"]:
            return Response(
                {"error": "Invalid kot_status. Choose: Pending, Sent, Prepared."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.kot_status = new_status
        item.save(update_fields=["kot_status"])
        return Response(
            {
                "message": f"Item kot_status updated to {new_status}.",
                "item": OrderItemSerializer(item).data,
            }
        )

    @extend_schema(
        summary="Initiate payment",
        responses={
            200: OpenApiResponse(description="Payment payload"),
            400: OpenApiResponse(description="Already paid"),
        },
    )
    @action(detail=True, methods=["post"], url_path="initiate_payment")
    def initiate_payment(self, request, pk=None):
        order = self.get_object()
        if order.payment_status == "Completed":
            return Response(
                {"error": "Order is already paid."}, status=status.HTTP_400_BAD_REQUEST
            )
        payment_data = self._get_payment_payload(order)
        if isinstance(payment_data, Response):
            return payment_data
        return Response({"message": "Payment payload ready.", **payment_data})

    @extend_schema(
        summary="eSewa success callback",
        auth=[],
        parameters=[OpenApiParameter("data", str, required=True)],
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Invalid signature or data"),
            402: OpenApiResponse(description="Payment not completed"),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="esewa_success",
        permission_classes=[AllowAny],
    )
    def esewa_success(self, request):
        decoded = self._decode_esewa_data(request.query_params.get("data"))
        if isinstance(decoded, Response):
            return decoded
        if not verify_esewa_signature(decoded, settings.ESEWA_SETTINGS["SECRET_KEY"]):
            return Response(
                {"error": "Signature verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order = get_object_or_404(Order, order_code=decoded.get("transaction_uuid"))
        if decoded.get("status") == "COMPLETE":
            order.payment_status = "Completed"
            order.order_status = "New"
            order.transaction_id = decoded.get("transaction_code")
            order.payment_response = decoded
            order.save()
            return Response(
                {"message": "Payment successful.", "order": OrderSerializer(order).data}
            )
        order.payment_status = "Failed"
        order.payment_response = decoded
        order.save()
        return Response(
            {"error": "Payment not completed by eSewa."},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    @extend_schema(
        summary="eSewa failure callback",
        auth=[],
        parameters=[OpenApiParameter("transaction_uuid", str, required=False)],
        responses={402: OpenApiResponse(description="Payment failed")},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="esewa_failure",
        permission_classes=[AllowAny],
    )
    def esewa_failure(self, request):
        order = Order.objects.filter(
            order_code=request.query_params.get("transaction_uuid")
        ).first()
        if order:
            order.payment_status = "Failed"
            order.save()
        return Response(
            {"error": "Payment failed or was cancelled."},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    def _get_payment_payload(self, order):
        try:
            return get_payment_strategy(order.payment_method).get_payment_payload(order)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _decode_esewa_data(self, encoded):
        if not encoded:
            return Response(
                {"error": "Missing data parameter."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            return json.loads(base64.b64decode(encoded).decode("utf-8"))
        except Exception:
            return Response(
                {"error": "Invalid base64 or JSON data."},
                status=status.HTTP_400_BAD_REQUEST,
            )
