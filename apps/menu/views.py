from rest_framework import viewsets
from rest_framework.permissions import BasePermission, AllowAny
from apps.menu.models import MenuItem, Category,Table
from apps.menu.serializers import CategorySerializer,MenuItemSerializer,TableSerializer

class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name='Owner').exists()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.select_related('location').all()
    serializer_class = TableSerializer
    permission_classes = [AllowAny]