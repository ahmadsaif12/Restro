from rest_framework import serializers
from .models import InventoryCategory, InventoryItem, MenuItemIngredient, StockTransaction
from apps.menu.models import MenuItem

class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = "__all__"
class InventoryItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=InventoryCategory.objects.all()
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    total_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "unit",
            "current_stock",
            "min_stock",
            "unit_cost",
            "supplier",
            "last_updated",
            "is_low_stock",
            "total_value",
        ]
        read_only_fields = ["last_updated"]

class MenuItemIngredientSerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(
        source="inventory_item.name", read_only=True
    )
    unit = serializers.CharField(source="inventory_item.unit", read_only=True)
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = MenuItemIngredient
        fields = [
            "id", "menu_item", "menu_item_name",
            "inventory_item", "inventory_item_name",
            "unit", "quantity_per_serving",
        ]

class StockTransactionSerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(
        source="inventory_item.name", read_only=True
    )
    class Meta:
        model = StockTransaction
        fields = [
            "id", "inventory_item", "inventory_item_name",
            "transaction_type", "quantity", "note", "created_at",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        transaction = super().create(validated_data)
        # Update InventoryItem.current_stock automatically
        item = transaction.inventory_item
        item.current_stock += transaction.quantity
        item.save()
        return transaction


# Read-only: show all ingredients for a given menu item
class MenuItemWithIngredientsSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    ingredients = MenuItemIngredientSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        from apps.menu.models import MenuItem
        model = MenuItem
        fields = ["id", "name", "category", "category_name", "price", "ingredients"]