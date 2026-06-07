"""
User Admin — configuração do Django Admin para User.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html

from dizimus.apps.users.models.user  import User
from .actions import make_active, make_inactive, export_to_csv
from .filters import HasPhotoFilter


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # ── Formulários ──────────────────────────────────────────────────────────
    form = UserChangeForm
    add_form = UserCreationForm

    # ── Lista ────────────────────────────────────────────────────────────────
    list_display = (
        "avatar_thumbnail",
        "email",
        "role_badge",
        "phone",
        "is_active_icon",
        "is_trusty",
        "is_staff",
        "date_joined",
    )
    list_display_links = ("avatar_thumbnail", "email")
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_trusty",
        "is_superuser",
        HasPhotoFilter,
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
    list_per_page = 25
    list_select_related = True
    save_on_top = True
    actions = [make_active, make_inactive, export_to_csv]

    # ── Fieldsets (edição) ───────────────────────────────────────────────────
    fieldsets = (
        (
            "Credenciais",
            {"fields": ("email", "password"), "classes": ("wide",)},
        ),
        (
            "Dados pessoais",
            {
                "fields": (
                    ("first_name", "last_name"),
                    "role",
                    "phone",
                    "photo",
                    "photo_preview",
                ),
            },
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_trusty",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Informações do sistema",
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # ── Fieldsets (criação) ──────────────────────────────────────────────────
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # ── Somente leitura ──────────────────────────────────────────────────────
    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
        "photo_preview",
    )

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="")
    def avatar_thumbnail(self, obj):
        url = obj.photo_url
        return format_html(
            '<img src="{}" width="36" height="36" '
            'style="border-radius:50%;object-fit:cover;border:2px solid #e0e0e0;" />',
            url,
        )

    @admin.display(description="Foto (prévia)")
    def photo_preview(self, obj):
        url = obj.photo_url
        return format_html(
            '<img src="{}" width="120" height="120" '
            'style="border-radius:8px;object-fit:cover;" />',
            url,
        )

    @admin.display(description="Tipo", ordering="role")
    def role_badge(self, obj):
        colors = {
            User.UserRole.MEMBER: ("#2563eb", "#dbeafe"),
            User.UserRole.CHURCH: ("#7c3aed", "#ede9fe"),
            User.UserRole.ADMIN: ("#dc2626", "#fee2e2"),
            
        }
        fg, bg = colors.get(obj.role, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, obj.get_role_display(),
        )

    @admin.display(description="Ativo", boolean=False, ordering="is_active")
    def is_active_icon(self, obj):
        icon, color = ("✅", "green") if obj.is_active else ("🚫", "red")
        return format_html('<span style="color:{};">{}</span>', color, icon)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    def save_model(self, request, obj, form, change):
        if not change:
            obj._created_by_admin = request.user
        super().save_model(request, obj, form, change)