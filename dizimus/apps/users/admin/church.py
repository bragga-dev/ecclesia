"""
Church Admin — configuração do Django Admin para Church.
"""
from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from dizimus.apps.community.models.member_church_model import MemberChurch
from dizimus.apps.users.models.church import Church
from .actions import verify_churches, unverify_churches, refresh_member_counts, export_to_csv
from .filters import ChurchVerifiedFilter, HasAsaasTokenFilter
from .inlines import ChurchAddressInline, MemberChurchInline


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    # ── Lista ────────────────────────────────────────────────────────────────
    list_display = (
        "banner_thumbnail",
        "name",
        "cnpj_display",
        "verified_badge",
        "total_members",
        "has_asaas_icon",
        "has_instagram",
        "has_website",
        "user__email",
    )
    list_display_links = ("banner_thumbnail", "name")
    list_filter = (
        ChurchVerifiedFilter,
        HasAsaasTokenFilter,
        "user__is_active",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "cnpj",
    )
    autocomplete_fields = ("user",)
    ordering = ("user__first_name",)
    list_per_page = 20
    save_on_top = True
    inlines = [ChurchAddressInline, MemberChurchInline]
    actions = [verify_churches, unverify_churches, refresh_member_counts, export_to_csv]

    # ── Fieldsets ────────────────────────────────────────────────────────────
    fieldsets = (
        (
            "Conta vinculada",
            {"fields": ("user",)},
        ),
        (
            "Identidade",
            {
                "fields": (
                    "cnpj",
                    "is_verified",
                    "total_members",
                    "banner",
                    "banner_preview",
                ),
            },
        ),
        (
            "Sobre a Igreja",
            {
                "fields": ("about", "instagram", "website"),
                "classes": ("collapse",),
            },
        ),
        (
            "Integração Asaas",
            {
                "fields": ("asaas_token",),
                "classes": ("collapse",),
                "description": "⚠️ O token é criptografado no banco. Edite com cuidado.",
            },
        ),
    )

    readonly_fields = ("total_members", "banner_preview")

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="")
    def banner_thumbnail(self, obj):
        return format_html(
            '<img src="{}" width="60" height="36" '
            'style="border-radius:4px;object-fit:cover;" />',
            obj.banner_url,
        )

    @admin.display(description="Igreja", ordering="user__first_name")
    def name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="CNPJ")
    def cnpj_display(self, obj):
        return obj.cnpj or "—"

    @admin.display(description="Verificada", ordering="is_verified")
    def verified_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background:#d1fae5;color:#065f46;padding:2px 10px;'
                'border-radius:12px;font-size:11px;font-weight:600;">✔ Verificada</span>'
            )
        return format_html(
            '<span style="background:#fef3c7;color:#92400e;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">⏳ Pendente</span>'
        )

    @admin.display(description="Asaas", boolean=True)
    def has_asaas_icon(self, obj):
        return bool(obj.asaas_token)

    @admin.display(description="Instagram", boolean=True)
    def has_instagram(self, obj):
        return bool(obj.instagram)

    @admin.display(description="Site", boolean=True)
    def has_website(self, obj):
        return bool(obj.website)

    @admin.display(description="E-mail", ordering="user__email")
    def user__email(self, obj):
        return obj.user.email

    @admin.display(description="Banner (prévia)")
    def banner_preview(self, obj):
        return format_html(
            '<img src="{}" style="max-width:400px;border-radius:8px;" />',
            obj.banner_url,
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .annotate(active_members=Count(
                "member_memberships",
                filter=Q(member_memberships__status=MemberChurch.Status.ACTIVE),
            ))
        )