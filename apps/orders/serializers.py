# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_name",
            "quantity",
            "unit_price",
            "subtotal",
            "kot_status",
            "notes",
        ]
        read_only_fields = [
            "unit_price",
            "kot_status",
        ]  # unit_price snapshotted on save


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_code",
            "user",
            "table",
            "order_status",
            "payment_method",
            "payment_status",
            "total_amount",
            "transaction_id",
            "payment_response",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "order_code",
            "user",
            "payment_status",
            "total_amount",
            "transaction_id",
            "payment_response",
            # 'order_status' is intentionally NOT read-only so staff can update it
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            # unit_price is snapshotted inside OrderItem.save()

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Smart update: preserve kot_status for existing items,
            # only add new ones and remove items no longer in the list
            existing_items = {item.menu_item_id: item for item in instance.items.all()}
            incoming_ids = {item_data["menu_item"].id for item_data in items_data}

            # Delete items removed from the order
            for menu_item_id, item in existing_items.items():
                if menu_item_id not in incoming_ids:
                    item.delete()

            # Update existing or create new items
            for item_data in items_data:
                menu_item_id = item_data["menu_item"].id
                if menu_item_id in existing_items:
                    # Update quantity/notes but preserve kot_status and unit_price
                    existing_item = existing_items[menu_item_id]
                    existing_item.quantity = item_data.get(
                        "quantity", existing_item.quantity
                    )
                    existing_item.notes = item_data.get("notes", existing_item.notes)
                    existing_item.save()
                else:
                    # New item — unit_price snapshotted in OrderItem.save()
                    OrderItem.objects.create(order=instance, **item_data)

        return instance
