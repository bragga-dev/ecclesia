"""
Church Admin — configuração do Django Admin para Church.
"""
from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.church import Church
from .actions import verify_churches, unverify_churches, refresh_member_counts, export_to_csv
from .filters import ChurchVerifiedFilter, HasAsaasTokenFilter
from .inlines import ChurchAddressInline, MemberChurchInline


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    # ── Lista ────────────────────────────────────────────────────────────────
    list_display = (
        "banner_thumbnail",
        "full_name_display",
        "cnpj_display",
        "verified_badge",
        "total_members",
        "phone",
        "has_asaas_icon",
        "has_instagram",
        "has_website",
        "user__email",
        "church_type_badge",
    )
    list_display_links = ("banner_thumbnail", "full_name_display")
    list_filter = (
        ChurchVerifiedFilter,
        HasAsaasTokenFilter,
        "user__is_active",
        "church_type",
    )
    search_fields = (
        "full_name",
        "user__email",
        "cnpj",
    )
    autocomplete_fields = ("user", "parent_church")
    ordering = ("full_name",)
    list_per_page = 20
    save_on_top = True
    inlines = [ChurchAddressInline, MemberChurchInline]
    actions = [verify_churches, unverify_churches, refresh_member_counts, export_to_csv]
    readonly_fields = ("slug", "banner_preview")

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
                    "full_name",
                    "cnpj",
                    ("church_type", "parent_church"),
                    "is_verified",
                    "total_members",
                    "slug",
                ),
            },
        ),
        (
            "Contato",
            {
                "fields": (
                    "phone",
                    "instagram",
                    "website",
                ),
            },
        ),
        (
            "Sobre a Igreja",
            {
                "fields": ("about", "banner", "banner_preview"),
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

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="")
    def banner_thumbnail(self, obj):
        return format_html(
            '<img src="{}" width="60" height="36" '
            'style="border-radius:4px;object-fit:cover;" />',
            obj.banner_url,
        )

    @admin.display(description="Igreja", ordering="full_name")
    def full_name_display(self, obj):
        return obj.full_name or f"Igreja {str(obj.id)[:8]}"

    @admin.display(description="CNPJ")
    def cnpj_display(self, obj):
        return obj.cnpj or "—"

    @admin.display(description="Telefone")
    def phone(self, obj):
        return str(obj.phone) if obj.phone else "—"

    @admin.display(description="Tipo")
    def church_type_badge(self, obj):
        colors = {
            Church.ChurchType.HEADQUARTERS: ("#1e40af", "#dbeafe"),
            Church.ChurchType.COMMUNITY: ("#15803d", "#dcfce7"),
            Church.ChurchType.INDEPENDENT: ("#6b7280", "#f3f4f6"),
        }
        fg, bg = colors.get(obj.church_type, ("#374151", "#f3f4f6"))
        return mark_safe(
            f'<span style="background:{bg};color:{fg};padding:2px 10px;'
            f'border-radius:12px;font-size:11px;font-weight:600;">'
            f'{obj.get_church_type_display()}</span>'
        )

    @admin.display(description="Verificada")  # ← Removido boolean=True
    def verified_badge(self, obj):
        if obj.is_verified:
            return mark_safe(
                '<span style="background:#d1fae5;color:#065f46;padding:2px 10px;'
                'border-radius:12px;font-size:11px;font-weight:600;">✔ Verificada</span>'
            )
        return mark_safe(
            '<span style="background:#fef3c7;color:#92400e;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">⏳ Pendente</span>'
        )

    @admin.display(description="Asaas", boolean=True)
    def has_asaas_icon(self, obj):
        return bool(obj.asaas_token and obj.asaas_token.strip())

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
            .select_related("user", "parent_church")
            .annotate(active_members=Count(
                "member_memberships",
                filter=Q(member_memberships__status=MemberChurch.Status.ACTIVE),
            ))
        )

    def save_model(self, request, obj, form, change):
        # Garante que o slug seja gerado
        if not obj.slug:
            obj.save()
        else:
            super().save_model(request, obj, form, change)