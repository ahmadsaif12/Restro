from django.contrib import admin
from apps.menu.models import Category, MenuItem,Table, TableLocation

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_available')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(TableLocation)
class TableLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'capacity', 'is_available')
    list_filter = ('location', 'is_available')  # filter by location and availability
    search_fields = ('name',)
    ordering = ('id',)