"""
AuditLog Admin — configuração do Django Admin para AuditLog.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter

from ecclesia.apps.users.models.audit_user_model import AuditLog


class PerformedByFilter(SimpleListFilter):
    """Filtro para saber se o log foi realizado por um usuário ou pelo sistema."""
    title = "Realizado por"
    parameter_name = "performed_by"

    def lookups(self, request, model_admin):
        return (
            ("user", "Usuário"),
            ("system", "Sistema"),
        )

    def queryset(self, request, queryset):
        if self.value() == "user":
            return queryset.filter(performed_by__isnull=False)
        if self.value() == "system":
            return queryset.filter(performed_by__isnull=True)
        return queryset


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "user_email",
        "performed_by_email",
        "timestamp_display",
        "has_details",
        "reason_preview",
    )
    list_filter = (
        "action",
        "timestamp",
        PerformedByFilter,  # Usa o filtro personalizado
    )
    search_fields = (
        "action",
        "user__email",
        "performed_by__email",
        "reason",
    )
    ordering = ("-timestamp",)
    list_per_page = 30
    date_hierarchy = "timestamp"
    readonly_fields = (
        "id",
        "action",
        "user",
        "performed_by",
        "timestamp",
        "details",
        "reason",
    )

    fieldsets = (
        (
            "Informações do Log",
            {
                "fields": (
                    "id",
                    "action",
                    ("user", "performed_by"),
                    "reason",
                    "timestamp",
                ),
            },
        ),
        (
            "Detalhes",
            {
                "fields": ("details",),
                "classes": ("collapse",),
            },
        ),
    )

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="Usuário", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Realizado por", ordering="performed_by__email")
    def performed_by_email(self, obj):
        if obj.performed_by:
            return obj.performed_by.email
        return "— (sistema)"

    @admin.display(description="Data/Hora", ordering="timestamp")
    def timestamp_display(self, obj):
        return obj.timestamp.strftime("%d/%m/%Y %H:%M:%S")

    @admin.display(description="Detalhes", boolean=True)
    def has_details(self, obj):
        return bool(obj.details)

    @admin.display(description="Motivo")
    def reason_preview(self, obj):
        if obj.reason:
            return obj.reason[:50] + "..." if len(obj.reason) > 50 else obj.reason
        return "—"

    # ── Permissões ───────────────────────────────────────────────────────────
    def has_add_permission(self, request):
        """Logs só podem ser criados pelo sistema, não manualmente."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permite apenas superusers deletarem logs."""
        return request.user.is_superuser