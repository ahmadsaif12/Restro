from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.menu.models import Category, MenuItem, Table, TableLocation


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name",)
    list_per_page = 10

    def get_model_perms(self, request):
        return {}


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ("id", "name", "category", "price", "is_available")
    fields = ("category", "name", "price", "is_available", "description")


@admin.register(TableLocation)
class TableLocationAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)
    list_per_page = 10

    def get_model_perms(self, request):
        return {}


@admin.register(Table)
class TableAdmin(ModelAdmin):
    list_display = ("id", "name", "location", "capacity", "is_available")
    list_filter = ("location", "is_available")
    search_fields = ("name",)
    ordering = ("id",)
    list_per_page = 10

    def get_model_perms(self, request):
        return {}
