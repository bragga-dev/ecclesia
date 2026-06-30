"""
Member Admin — configuração do Django Admin para Member.
"""
from datetime import date
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ecclesia.apps.users.models.member import Member
from ecclesia.apps.community.models.member_church_model import MemberChurch

from .actions import export_members_csv
from .filters import AgeRangeFilter, MembershipStatusFilter, HasPhotoFilter
from .inlines import MemberAddressInline, MemberMembershipInline


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "avatar_thumbnail",
        "full_name",
        "username",
        "email",
        "cpf_masked",
        "date_of_birth",
        "age",
        "churches_count",
        "phone",
        "primary_role",
    )
    list_display_links = ("avatar_thumbnail", "full_name")
    list_filter = (
        AgeRangeFilter,
        MembershipStatusFilter,
        "user__is_active",
        HasPhotoFilter,
    )
    search_fields = (
        "first_name",
        "last_name",
        "username",
        "user__email",
        "cpf",
    )
    autocomplete_fields = ("user",)
    ordering = ("first_name",)
    list_per_page = 25
    save_on_top = True
    inlines = [MemberAddressInline, MemberMembershipInline]
    actions = [export_members_csv]
    readonly_fields = ("slug",)

    fieldsets = (
        (
            "Conta vinculada",
            {"fields": ("user",)},
        ),
        (
            "Dados pessoais",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    ("cpf", "date_of_birth"),
                    "phone",
                    "slug",
                ),
            },
        ),
    )

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="")
    def avatar_thumbnail(self, obj):
        return format_html(
            '<img src="{}" width="36" height="36" '
            'style="border-radius:50%%;object-fit:cover;border:2px solid #e0e0e0;" />',
            obj.user.photo_url,
        )

    @admin.display(description="Nome", ordering="first_name")
    def full_name(self, obj):
        return obj.get_full_name()

    @admin.display(description="Usuário", ordering="username")
    def username(self, obj):
        return obj.username or "—"

    @admin.display(description="E-mail", ordering="user__email")
    def email(self, obj):
        return obj.user.email

    @admin.display(description="Telefone")
    def phone(self, obj):
        return str(obj.phone) if obj.phone else "—"

    @admin.display(description="CPF")
    def cpf_masked(self, obj):
        if not obj.cpf:
            return "—"
        raw = obj.cpf.replace(".", "").replace("-", "")
        if len(raw) == 11:
            return f"***.***.{raw[6:9]}-{raw[9:]}"
        return obj.cpf

    @admin.display(description="Idade")
    def age(self, obj):
        if not obj.date_of_birth:
            return "—"
        today = date.today()
        dob = obj.date_of_birth
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return f"{years} anos"

    @admin.display(description="Igrejas", ordering="churches_count")
    def churches_count(self, obj):
        count = getattr(obj, "churches_count", 0)
        return format_html(
            '<span style="font-weight:600;color:#4f46e5;">{}</span>', count
        )

    @admin.display(description="Função principal")
    def primary_role(self, obj):
        """Retorna a função do membro na igreja principal (a mais recente ativa)"""
        primary = obj.church_memberships.filter(
            status=MemberChurch.Status.ACTIVE
        ).first()
        if primary:
            return primary.get_role_display()
        return "—"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .annotate(churches_count=Count("church_memberships"))
        )

    def save_model(self, request, obj, form, change):
        # Garante que o slug seja gerado
        if not obj.slug:
            obj.save()
        else:
            super().save_model(request, obj, form, change)