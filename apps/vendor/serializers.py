from rest_framework import serializers
from django.db import models as django_models
from .models import Vendor, Purchase


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            "id",
            "purchase_amount",
            "invoice_number",
            "notes",
            "description",
            "is_paid",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RecordPurchaseSerializer(serializers.Serializer):
    vendor_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    purchase_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    invoice_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    description = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        vendor, _ = Vendor.objects.get_or_create(
            vendor_name=validated_data["vendor_name"],
            defaults={
                "phone_number": validated_data.get("phone_number", ""),
                "email": validated_data.get("email", ""),
                "address": validated_data.get("address", ""),
            },
        )
        return Purchase.objects.create(
            vendor=vendor,
            purchase_amount=validated_data["purchase_amount"],
            invoice_number=validated_data.get("invoice_number", ""),
            description=validated_data.get("description", ""),
            notes=validated_data.get("notes", ""),
        )


class VendorListSerializer(serializers.ModelSerializer):
    total_purchases = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_paid = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_pending = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_settled = serializers.BooleanField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "vendor_name",
            "phone_number",
            "email",
            "address",
            "total_purchases",
            "total_paid",
            "total_pending",
            "is_settled",
            "last_activity",
        ]


class VendorDetailSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True, read_only=True)
    total_purchases = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_paid = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_pending = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_settled = serializers.BooleanField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "vendor_name",
            "phone_number",
            "email",
            "address",
            "total_purchases",
            "total_paid",
            "total_pending",
            "is_settled",
            "last_activity",
            "purchases",
        ]


class DashboardSerializer(serializers.Serializer):
    total_pending = serializers.DecimalField(max_digits=10, decimal_places=2)
    vendors_with_pending = serializers.IntegerField()
    total_vendors = serializers.IntegerField()
