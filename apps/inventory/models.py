from django.db import models
from apps.menu.models import MenuItem


from django.utils.text import slugify

class InventoryCategory(models.Model):
    """
    Inventory categories (e.g., Meat, Dairy, Vegetables).
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Inventory Categories"


class InventoryItem(models.Model):
    """
    A raw ingredient or supply item tracked in stock.
    """
    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Litre"),
        ("ml", "Millilitre"),
        ("pcs", "Pieces"),
        ("dozen", "Dozen"),
        ("box", "Box"),
    ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="kg")
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    min_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock

    @property
    def total_value(self):
        return self.current_stock * self.unit_cost

    class Meta:
        ordering = ["name"]


class MenuItemIngredient(models.Model):
    """
    Junction table: links a MenuItem to the InventoryItems it uses,
    with the quantity consumed per serving.

    Example: "Chicken Momo" uses 0.150 kg of Chicken Breast per serving.
    """
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="used_in_menu_items",
    )
    quantity_per_serving = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="How much of this ingredient is used per one serving of the menu item",
    )

    def __str__(self):
        return (
            f"{self.menu_item.name} → "
            f"{self.quantity_per_serving} {self.inventory_item.unit} "
            f"of {self.inventory_item.name}"
        )

    class Meta:
        unique_together = ("menu_item", "inventory_item")


class StockTransaction(models.Model):
    """
    Audit log of every stock change (restock, usage, waste, adjustment).
    """
    TRANSACTION_TYPES = [
        ("restock", "Restock"),
        ("usage", "Usage"),       # consumed when an order is placed
        ("waste", "Waste"),
        ("adjustment", "Manual Adjustment"),
    ]

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="Positive = added to stock, Negative = removed from stock",
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} | {self.inventory_item.name} | {self.quantity}"

    class Meta:
        ordering = ["-created_at"]