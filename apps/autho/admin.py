from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html

from apps.autho.models import AuthorProfile
from unfold.admin import ModelAdmin

User = get_user_model()


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "full_name", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        custom_classes = (
            "border border-base-200 bg-white font-medium min-w-20 placeholder-base-400 "
            "rounded-default shadow-xs text-sm focus:outline-2 focus:-outline-offset-2 "
            "focus:outline-primary-600 dark:bg-base-900 dark:border-base-700 px-3 py-2 w-full"
        )

        self.fields["password1"].widget.attrs.update({"class": custom_classes})
        self.fields["password2"].widget.attrs.update({"class": custom_classes})


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "avatar_preview",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "full_name")
    list_display_links = ("id", "email")
    ordering = ("email",)
    list_per_page = 10

    fieldsets = (
        (
            "Personal Info",
            {
                "fields": ("email", "full_name", "role"),
                "classes": ("wide",),
            },
        ),
        (
            "Authentication",
            {
                "fields": ("password",),
                "classes": ("wide",),
            },
        ),
        (
            "Permissions",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
                "classes": ("wide",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ("last_login",)

    def avatar_preview(self, obj):
        if hasattr(obj, "avatar") and obj.avatar:
            try:
                return format_html(
                    '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:50%;" />',
                    obj.avatar.url,
                )
            except Exception:
                return "Error"
        return "N/A"

    avatar_preview.short_description = "Photo"
