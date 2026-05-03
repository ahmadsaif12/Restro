from django.db import models
from django.conf import settings
from apps.menu.models import MenuItem, Table
from apps.misc.models import BaseModel
import random
import string

def generate_order_code():
    return ''.join(random.choices(string.digits, k=6))

class Order(BaseModel):
    PAYMENT_METHODS = (
        ('eSewa', 'eSewa'),
        ('Khalti', 'Khalti'),
        ('COD', 'Cash on Delivery'),
    )

    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    ORDER_STATUS = (
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Ready', 'Ready'),
        ('Served', 'Served'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    )

    order_code = models.CharField(max_length=10, unique=True, default=generate_order_code)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders'
    )

    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders'
    )

    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='New')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_response = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True) # e.g. "no onion, extra spicy" 

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ORD-{self.order_code} ({self.table})"

    def save(self, *args, **kwargs):
        # Sync table availability when order is closed
        if self.table:
            if self.order_status in ('Paid', 'Cancelled'):
                self.table.is_available = True
            else:
                self.table.is_available = False
            self.table.save(update_fields=['is_available'])
        super().save(*args, **kwargs)

    def recalculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=['total_amount'])


class OrderItem(BaseModel):
    KOT_STATUS = (
        ('Pending', 'Pending'),    
        ('Sent', 'Sent'),          
        ('Prepared', 'Prepared'), 
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,  
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) 
    kot_status = models.CharField(max_length=20, choices=KOT_STATUS, default='Pending')
    notes = models.CharField(max_length=200, blank=True) 

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity} — ORD-{self.order.order_code}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Snapshot menu item price at the time of ordering
        if not self.pk and not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)