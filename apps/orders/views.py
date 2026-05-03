from __future__ import annotations
import base64, json

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order
from .serializers import OrderSerializer
from .payment_strategies import get_payment_strategy
from .utils import verify_esewa_signature

ALLOWED_UPDATE_FIELDS = {'order_status', 'payment_status', 'table_number', 'notes'}


@extend_schema_view(
    list=extend_schema(summary="List orders", parameters=[
        OpenApiParameter("order_status", str), OpenApiParameter("payment_status", str),
        OpenApiParameter("payment_method", str), OpenApiParameter("search", str), OpenApiParameter("ordering", str),
    ]),
    retrieve=extend_schema(summary="Retrieve order"),
    destroy=extend_schema(summary="Delete order"),
)
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order_status', 'payment_status', 'payment_method']
    search_fields = ['order_code', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('items__menu_item').order_by('-created_at')

    @extend_schema(summary="Create order", request=OrderSerializer, responses={201: OrderSerializer})
    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)
        order.recalculate_total()
        payment_data = self._get_payment_payload(order)
        if isinstance(payment_data, Response):
            return payment_data
        return Response({"message": "Order created.", "order": OrderSerializer(order).data, **payment_data}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Update order (allowed: order_status, payment_status, table_number, notes)",
        request=inline_serializer("OrderPutRequest", fields={
            "order_status": serializers.CharField(required=False),
            "payment_status": serializers.CharField(required=False),
            "table_number": serializers.CharField(required=False),
            "notes": serializers.CharField(required=False),
        }),
        responses={200: OrderSerializer, 400: OpenApiResponse(description="No valid fields")},
    )
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        filtered_data = {k: v for k, v in request.data.items() if k in ALLOWED_UPDATE_FIELDS}
        if not filtered_data:
            return Response({"error": f"Allowed fields: {sorted(ALLOWED_UPDATE_FIELDS)}"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(order, data=filtered_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Order updated.", "order": serializer.data})

    @extend_schema(summary="Initiate payment", responses={200: OpenApiResponse(description="Payment payload"), 400: OpenApiResponse(description="Already paid")})
    @action(detail=True, methods=['post'], url_path='initiate_payment')
    def initiate_payment(self, request, pk=None):
        order = self.get_object()
        if order.payment_status == 'Completed':
            return Response({"error": "Already paid."}, status=status.HTTP_400_BAD_REQUEST)
        payment_data = self._get_payment_payload(order)
        if isinstance(payment_data, Response):
            return payment_data
        return Response({"message": "Payment payload ready.", **payment_data})

    @extend_schema(summary="eSewa success callback", auth=[],
        parameters=[OpenApiParameter("data", str, required=True)],
        responses={200: OrderSerializer, 400: OpenApiResponse(description="Invalid"), 402: OpenApiResponse(description="Not completed")},
    )
    @action(detail=False, methods=['get'], url_path='esewa_success', permission_classes=[AllowAny])
    def esewa_success(self, request):
        decoded = self._decode_esewa_data(request.query_params.get('data'))
        if isinstance(decoded, Response):
            return decoded
        if not verify_esewa_signature(decoded, settings.ESEWA_SETTINGS["SECRET_KEY"]):
            return Response({"error": "Signature failed."}, status=status.HTTP_400_BAD_REQUEST)
        order = get_object_or_404(Order, order_code=decoded.get('transaction_uuid'))
        if decoded.get('status') == 'COMPLETE':
            order.payment_status, order.order_status = 'Completed', 'New'
            order.transaction_id, order.payment_response = decoded.get('transaction_code'), decoded
            order.save()
            return Response({"message": "Payment successful.", "order": OrderSerializer(order).data})
        order.payment_status, order.payment_response = 'Failed', decoded
        order.save()
        return Response({"error": "Payment not completed."}, status=status.HTTP_402_PAYMENT_REQUIRED)

    @extend_schema(summary="eSewa failure callback", auth=[],
        parameters=[OpenApiParameter("transaction_uuid", str, required=False)],
        responses={402: OpenApiResponse(description="Payment failed")},
    )
    @action(detail=False, methods=['get'], url_path='esewa_failure', permission_classes=[AllowAny])
    def esewa_failure(self, request):
        order = Order.objects.filter(order_code=request.query_params.get('transaction_uuid')).first()
        if order:
            order.payment_status = 'Failed'
            order.save()
        return Response({"error": "Payment failed."}, status=status.HTTP_402_PAYMENT_REQUIRED)

    def _get_payment_payload(self, order):
        try:
            return get_payment_strategy(order.payment_method).get_payment_payload(order)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _decode_esewa_data(self, encoded):
        if not encoded:
            return Response({"error": "No data."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            return json.loads(base64.b64decode(encoded).decode('utf-8'))
        except Exception:
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)