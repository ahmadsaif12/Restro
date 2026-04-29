from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer

from apps.menu.models import MenuItem, Category, Table
from apps.menu.serializers import CategorySerializer, MenuItemSerializer, TableSerializer


def not_found():
    return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


# ── Categories (sirf GET — dropdown ke liye) ─────────────────────────────────

class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all menu categories for dropdown",
        operation_id="menu_category_list",
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request):
        qs = Category.objects.filter(is_active=True)
        return Response(CategorySerializer(qs, many=True).data)

    @extend_schema(
        summary="Create menu category",
        operation_id="menu_category_create",
        request=CategorySerializer,
        responses={201: CategorySerializer}
    )
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Menu Items ────────────────────────────────────────────────────────────────

class MenuItemListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all menu items",
        operation_id="menu_item_list",
        parameters=[
            OpenApiParameter("search", str, description="Search by name"),
            OpenApiParameter("category", int, description="Filter by category ID"),
        ],
        responses={200: MenuItemSerializer(many=True)}
    )
    def get(self, request):
        qs = MenuItem.objects.select_related("category").all()
        search = request.query_params.get("search")
        category = request.query_params.get("category")
        if search:
            qs = qs.filter(name__icontains=search)
        if category:
            qs = qs.filter(category_id=category)
        return Response(MenuItemSerializer(qs, many=True).data)

    @extend_schema(
        summary="Add new menu item",
        operation_id="menu_item_create",
        request=inline_serializer(
            name="MenuItemCreateRequest",
            fields={
                "name": serializers.CharField(),
                "category": serializers.IntegerField(help_text="Category ID"),
                "price": serializers.DecimalField(max_digits=10, decimal_places=2),
                "description": serializers.CharField(required=False, allow_blank=True),
            }
        ),
        responses={201: MenuItemSerializer}
    )
    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return MenuItem.objects.select_related("category").get(pk=pk)
        except MenuItem.DoesNotExist:
            return None

    @extend_schema(
        summary="Update menu item",
        operation_id="menu_item_update",
        request=MenuItemSerializer,
        responses={200: MenuItemSerializer}
    )
    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return not_found()
        serializer = MenuItemSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete menu item",
        operation_id="menu_item_delete",
        responses={204: None}
    )
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return not_found()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Tables ────────────────────────────────────────────────────────────────────

class TableListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all tables",
        operation_id="table_list",
        responses={200: TableSerializer(many=True)}
    )
    def get(self, request):
        qs = Table.objects.select_related("location").all()
        return Response(TableSerializer(qs, many=True).data)

    @extend_schema(
        summary="Add new table",
        operation_id="table_create",
        request=TableSerializer,
        responses={201: TableSerializer}
    )
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Table.objects.select_related("location").get(pk=pk)
        except Table.DoesNotExist:
            return None

    @extend_schema(
        summary="Update table",
        operation_id="table_update",
        request=TableSerializer,
        responses={200: TableSerializer}
    )
    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return not_found()
        serializer = TableSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete table",
        operation_id="table_delete",
        responses={204: None}
    )
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return not_found()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)