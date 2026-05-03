# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'menu_item',
            'menu_item_name',
            'quantity',
            'unit_price',
            'subtotal',
            'kot_status',
            'notes',
        ]
        read_only_fields = ['unit_price', 'kot_status']  # unit_price snapshotted on save


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_code',
            'user',
            'table',
            'order_status',
            'payment_method',
            'payment_status',
            'total_amount',
            'transaction_id',
            'payment_response',
            'notes',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'order_code',
            'user',          
            'payment_status',
            'total_amount',  
            'transaction_id',
            'payment_response',
            'order_status',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            # unit_price is snapshotted inside OrderItem.save()

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance