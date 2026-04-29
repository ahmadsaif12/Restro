from django.urls import path
from .views import (
    CategoryListView,
    MenuItemListView,
    MenuItemDetailView,
    TableListView,
    TableDetailView,
)

urlpatterns = [
    path("categories/",       CategoryListView.as_view(),    name="menu-category-list"),
    path("items/",            MenuItemListView.as_view(),    name="menu-item-list"),
    path("items/<int:pk>/",   MenuItemDetailView.as_view(),  name="menu-item-detail"),
    path("tables/",           TableListView.as_view(),       name="table-list"),
    path("tables/<int:pk>/",  TableDetailView.as_view(),     name="table-detail"),
]