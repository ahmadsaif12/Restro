from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["unit_price"]

    def has_add_permission(self, request, obj=None):
        return obj is not None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def get_extra(self, request, obj=None, **kwargs):
        # Don't show empty rows
        return 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "order_code",
        "table",
        "order_status",
        "payment_status",
        "total_amount",
        "created_at",
    ]
    list_filter = ["order_status", "payment_status", "payment_method", "created_at"]
    search_fields = ["order_code", "table__number", "transaction_id"]
    inlines = [OrderItemInline]
    readonly_fields = [
        "order_code",
        "total_amount",
        "transaction_id",
        "payment_response",
    ]

    fieldsets = (
        ("Order Info", {"fields": ("order_code", "user", "table", "order_status")}),
        (
            "Payment Info",
            {
                "fields": (
                    "payment_method",
                    "payment_status",
                    "total_amount",
                    "transaction_id",
                    "payment_response",
                )
            },
        ),
        ("Notes", {"fields": ("notes",)}),
    )

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        return self.inlines

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id is None:
            original_inlines = self.inlines
            self.inlines = []
            try:
                response = super().changeform_view(
                    request, object_id, form_url, extra_context
                )
            finally:
                self.inlines = original_inlines
            return response
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ["menu_item", "order", "quantity", "unit_price", "kot_status"]
    list_filter = ["kot_status", "created_at"]
    search_fields = ["order__order_code", "menu_item__name"]

    def get_model_perms(self, request):
        return {}
