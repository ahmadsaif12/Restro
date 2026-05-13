from django.db import models

from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'
    )

    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    

class TableLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    name = models.CharField(max_length=50)  
    location = models.ForeignKey(
        TableLocation,
        on_delete=models.CASCADE,
        related_name='tables'
    )
    capacity = models.PositiveIntegerField(default=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.location.name})"