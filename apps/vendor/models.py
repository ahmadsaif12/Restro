from django.db import models
from apps.misc.models import BaseModel


class Vendor(BaseModel):
    vendor_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=50)

    def __str__(self):
        return self.vendor_name

    @property
    def total_purchases(self):
        return (
            self.purchases.aggregate(total=models.Sum("purchase_amount"))["total"] or 0
        )

    @property
    def total_paid(self):
        return (
            self.purchases.filter(is_paid=True).aggregate(
                total=models.Sum("purchase_amount")
            )["total"]
            or 0
        )

    @property
    def total_pending(self):
        return self.total_purchases - self.total_paid

    @property
    def is_settled(self):
        return self.total_pending == 0

    @property
    def last_activity(self):
        last = self.total_purchases.order_by("-created_at").first()
        return last.created_at if last else self.created_at


class Purchase(BaseModel):
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="purchases"
    )
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vendor.vendor_name} - {self.purchase_amount}"
