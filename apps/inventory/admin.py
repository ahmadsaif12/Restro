from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    InventoryCategory,
    InventoryItem,
    MenuItemIngredient,
    StockTransaction,
)


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

    def get_model_perms(self, request):
        return {}


@admin.register(InventoryItem)
class InventoryItemAdmin(ModelAdmin):
    list_display = (
        "name",
        "category",
        "unit",
        "current_stock",
        "min_stock",
        "unit_cost",
        "supplier",
        "last_updated",
        "is_low_stock",
        "total_value",
    )
    list_filter = ("category", "unit")
    search_fields = ("name", "supplier")
    ordering = ("name",)
    readonly_fields = ("last_updated", "is_low_stock", "total_value")


@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(ModelAdmin):
    list_display = (
        "menu_item",
        "inventory_item",
        "quantity_per_serving",
    )
    list_filter = ("menu_item", "inventory_item")
    search_fields = (
        "menu_item__name",
        "inventory_item__name",
    )

    def get_model_perms(self, request):
        return {}


@admin.register(StockTransaction)
class StockTransactionAdmin(ModelAdmin):
    list_display = (
        "inventory_item",
        "transaction_type",
        "quantity",
        "created_at",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = ("inventory_item__name", "note")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def get_model_perms(self, request):
        return {}
