"""
admin.py — Configuração avançada do Django Admin
Modelos: User, Church, ChurchAddress, Member, MemberAddress, MemberChurch
"""

import csv
from datetime import date
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (
    Church,
    ChurchAddress,
    Member,
    MemberAddress,
    MemberChurch,
    User,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Utilitários compartilhados
# ═══════════════════════════════════════════════════════════════════════════════

def export_to_csv(modeladmin, request, queryset):
    """Ação genérica: exporta os campos list_display do queryset para CSV."""
    meta        = modeladmin.model._meta
    field_names = [f.name for f in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{meta.verbose_name_plural}.csv"'

    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f, "") for f in field_names])
    return response

export_to_csv.short_description = "⬇ Exportar selecionados para CSV"


def make_active(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} usuário(s) ativado(s).", messages.SUCCESS)

make_active.short_description = "✅ Ativar usuários selecionados"


def make_inactive(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} usuário(s) desativado(s).", messages.WARNING)

make_inactive.short_description = "🚫 Desativar usuários selecionados"


# ═══════════════════════════════════════════════════════════════════════════════
# Inlines
# ═══════════════════════════════════════════════════════════════════════════════

class ChurchAddressInline(admin.StackedInline):
    model          = ChurchAddress
    extra          = 0
    min_num        = 0
    max_num        = 5
    can_delete     = True
    show_change_link = True
    fields         = (
        ("cep", "principal"),
        ("road", "number"),
        ("district", "city", "state"),
        "complement",
        "country",
    )
    readonly_fields = ("slug",)


class MemberAddressInline(admin.StackedInline):
    model          = MemberAddress
    extra          = 0
    min_num        = 0
    max_num        = 5
    can_delete     = True
    show_change_link = True
    fields         = (
        ("cep", "principal"),
        ("road", "number"),
        ("district", "city", "state"),
        "complement",
        "country",
    )
    readonly_fields = ("slug",)


class MemberChurchInline(admin.TabularInline):
    model            = MemberChurch
    fk_name          = "church"
    extra            = 0
    can_delete       = True
    show_change_link = True
    autocomplete_fields = ("member",)
    fields           = ("member", "status", "joined_at", "left_at")
    readonly_fields  = ("joined_at",)


class MemberMembershipInline(admin.TabularInline):
    model            = MemberChurch
    fk_name          = "member"
    extra            = 0
    can_delete       = True
    show_change_link = True
    autocomplete_fields = ("church",)
    fields           = ("church", "status", "joined_at", "left_at")
    readonly_fields  = ("joined_at",)


# ═══════════════════════════════════════════════════════════════════════════════
# Filtros personalizados
# ═══════════════════════════════════════════════════════════════════════════════

class HasPhotoFilter(admin.SimpleListFilter):
    title         = "Tem foto própria?"
    parameter_name = "has_photo"

    def lookups(self, request, model_admin):
        return (("yes", "Sim"), ("no", "Não"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(photo="").exclude(photo="default/user_img.jpg")
        if self.value() == "no":
            return queryset.filter(
                Q(photo="") | Q(photo="default/user_img.jpg") | Q(photo__isnull=True)
            )


class AgeRangeFilter(admin.SimpleListFilter):
    title          = "Faixa etária"
    parameter_name = "age_range"

    def lookups(self, request, model_admin):
        return (
            ("under18",  "Menor de 18"),
            ("18_35",    "18 – 35 anos"),
            ("36_60",    "36 – 60 anos"),
            ("over60",   "Acima de 60"),
            ("unknown",  "Não informado"),
        )

    def queryset(self, request, queryset):
        today = date.today()

        def age_cutoff(years):
            return today.replace(year=today.year - years)

        v = self.value()
        if v == "under18":
            return queryset.filter(date_of_birth__gt=age_cutoff(18))
        if v == "18_35":
            return queryset.filter(
                date_of_birth__lte=age_cutoff(18),
                date_of_birth__gte=age_cutoff(35),
            )
        if v == "36_60":
            return queryset.filter(
                date_of_birth__lte=age_cutoff(36),
                date_of_birth__gte=age_cutoff(60),
            )
        if v == "over60":
            return queryset.filter(date_of_birth__lt=age_cutoff(60))
        if v == "unknown":
            return queryset.filter(date_of_birth__isnull=True)


class MembershipStatusFilter(admin.SimpleListFilter):
    title          = "Status de vínculo"
    parameter_name = "membership_status"

    def lookups(self, request, model_admin):
        return MemberChurch.Status.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(church_memberships__status=self.value()).distinct()


class ChurchVerifiedFilter(admin.SimpleListFilter):
    title          = "Verificação"
    parameter_name = "verified"

    def lookups(self, request, model_admin):
        return (("yes", "Verificadas"), ("no", "Pendentes"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_verified=True)
        if self.value() == "no":
            return queryset.filter(is_verified=False)


class HasAsaasTokenFilter(admin.SimpleListFilter):
    title          = "Token Asaas"
    parameter_name = "has_asaas"

    def lookups(self, request, model_admin):
        return (("yes", "Configurado"), ("no", "Não configurado"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(asaas_token__isnull=True).exclude(asaas_token="")
        if self.value() == "no":
            return queryset.filter(Q(asaas_token__isnull=True) | Q(asaas_token=""))


# ═══════════════════════════════════════════════════════════════════════════════
# Admin — User
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # ── Formulários ──────────────────────────────────────────────────────────
    form     = UserChangeForm
    add_form = UserCreationForm

    # ── Lista ────────────────────────────────────────────────────────────────
    list_display = (
        "avatar_thumbnail",
        "email",
        "get_full_name",
        "username",
        "role_badge",
        "phone",
        "is_active_icon",
        "is_trusty",
        "is_staff",
        "date_joined",
    )
    list_display_links  = ("avatar_thumbnail", "email")
    list_filter         = (
        "role",
        "is_active",
        "is_staff",
        "is_trusty",
        "is_superuser",
        HasPhotoFilter,
        "date_joined",
    )
    search_fields       = ("email", "username", "first_name", "last_name", "phone")
    ordering            = ("-date_joined",)
    date_hierarchy      = "date_joined"
    list_per_page       = 25
    list_select_related = True
    save_on_top         = True
    actions             = [make_active, make_inactive, export_to_csv]

    # ── Fieldsets (edição) ───────────────────────────────────────────────────
    fieldsets = (
        (
            "Credenciais",
            {
                "fields": ("email", "password"),
                "classes": ("wide",),
            },
        ),
        (
            "Dados pessoais",
            {
                "fields": (
                    ("first_name", "last_name"),
                    "username",
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
                "fields": ("slug", "last_login", "date_joined", "created_at", "updated_at"),
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
                    "username",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # ── Somente leitura ──────────────────────────────────────────────────────
    readonly_fields = (
        "slug",
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
            # Registra quem criou via admin (log de auditoria básico)
            obj._created_by_admin = request.user
        super().save_model(request, obj, form, change)


# ═══════════════════════════════════════════════════════════════════════════════
# Admin — Church
# ═══════════════════════════════════════════════════════════════════════════════

def verify_churches(modeladmin, request, queryset):
    updated = queryset.update(is_verified=True)
    modeladmin.message_user(request, f"{updated} igreja(s) verificada(s).", messages.SUCCESS)

verify_churches.short_description = "✔ Verificar igrejas selecionadas"


def unverify_churches(modeladmin, request, queryset):
    updated = queryset.update(is_verified=False)
    modeladmin.message_user(request, f"{updated} igreja(s) marcada(s) como não verificadas.", messages.WARNING)

unverify_churches.short_description = "✖ Remover verificação das igrejas selecionadas"


def refresh_member_counts(modeladmin, request, queryset):
    for church in queryset:
        church.refresh_total_members()
    modeladmin.message_user(
        request,
        f"Contagem de membros atualizada para {queryset.count()} igreja(s).",
        messages.SUCCESS,
    )

refresh_member_counts.short_description = "🔄 Recalcular total de membros"


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
    list_display_links  = ("banner_thumbnail", "name")
    list_filter         = (
        ChurchVerifiedFilter,
        HasAsaasTokenFilter,
        "user__is_active",
    )
    search_fields       = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "cnpj",
    )
    autocomplete_fields = ("user",)
    ordering            = ("user__first_name",)
    list_per_page       = 20
    save_on_top         = True
    inlines             = [ChurchAddressInline, MemberChurchInline]
    actions             = [verify_churches, unverify_churches, refresh_member_counts, export_to_csv]

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


# ═══════════════════════════════════════════════════════════════════════════════
# Admin — ChurchAddress
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(ChurchAddress)
class ChurchAddressAdmin(admin.ModelAdmin):
    list_display   = ("church", "full_address", "city", "state", "cep", "principal")
    list_filter    = ("state", "principal")
    search_fields  = ("church__user__first_name", "church__user__last_name", "road", "city", "cep")
    ordering       = ("church__user__first_name", "city")
    list_per_page  = 30
    readonly_fields = ("slug",)

    fieldsets = (
        (
            "Igreja",
            {"fields": ("church", "principal")},
        ),
        (
            "Endereço",
            {
                "fields": (
                    "cep",
                    ("road", "number"),
                    ("district", "city", "state"),
                    "complement",
                    "country",
                    "slug",
                ),
            },
        ),
    )

    @admin.display(description="Endereço completo")
    def full_address(self, obj):
        return str(obj)


# ═══════════════════════════════════════════════════════════════════════════════
# Admin — Member
# ═══════════════════════════════════════════════════════════════════════════════

def export_members_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="membros.csv"'

    writer = csv.writer(response)
    writer.writerow(["Nome completo", "E-mail", "CPF", "Data de nascimento", "Telefone"])
    for m in queryset.select_related("user"):
        writer.writerow([
            m.user.get_full_name(),
            m.user.email,
            m.cpf or "—",
            m.date_of_birth.strftime("%d/%m/%Y") if m.date_of_birth else "—",
            str(m.user.phone) if m.user.phone else "—",
        ])
    return response

export_members_csv.short_description = "⬇ Exportar membros selecionados para CSV"


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "avatar_thumbnail",
        "full_name",
        "email",
        "cpf_masked",
        "date_of_birth",
        "age",
        "churches_count",
        "phone",
    )
    list_display_links  = ("avatar_thumbnail", "full_name")
    list_filter         = (
        AgeRangeFilter,
        MembershipStatusFilter,
        "user__is_active",
        HasPhotoFilter,
    )
    search_fields       = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "cpf",
    )
    autocomplete_fields = ("user",)
    ordering            = ("user__first_name",)
    date_hierarchy      = None  # data de nascimento não é DateTimeField; usar filter
    list_per_page       = 25
    save_on_top         = True
    inlines             = [MemberAddressInline, MemberMembershipInline]
    actions             = [export_members_csv]

    fieldsets = (
        (
            "Conta vinculada",
            {"fields": ("user",)},
        ),
        (
            "Dados pessoais",
            {
                "fields": ("cpf", "date_of_birth"),
            },
        ),
    )

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="")
    def avatar_thumbnail(self, obj):
        return format_html(
            '<img src="{}" width="36" height="36" '
            'style="border-radius:50%;object-fit:cover;border:2px solid #e0e0e0;" />',
            obj.user.photo_url,
        )

    @admin.display(description="Nome", ordering="user__first_name")
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="E-mail", ordering="user__email")
    def email(self, obj):
        return obj.user.email

    @admin.display(description="Telefone")
    def phone(self, obj):
        return str(obj.user.phone) if obj.user.phone else "—"

    @admin.display(description="CPF")
    def cpf_masked(self, obj):
        """Exibe CPF parcialmente mascarado: ***.***.###-##"""
        if not obj.cpf:
            return "—"
        # Mantém apenas os últimos 5 dígitos visíveis
        raw = obj.cpf.replace(".", "").replace("-", "")
        if len(raw) == 11:
            return f"***.***. {raw[6:9]}-{raw[9:]}"
        return obj.cpf

    @admin.display(description="Idade")
    def age(self, obj):
        if not obj.date_of_birth:
            return "—"
        today = date.today()
        dob   = obj.date_of_birth
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return f"{years} anos"

    @admin.display(description="Igrejas", ordering="churches_count")
    def churches_count(self, obj):
        count = getattr(obj, "churches_count", 0)
        return format_html(
            '<span style="font-weight:600;color:#4f46e5;">{}</span>', count
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .annotate(churches_count=Count("church_memberships"))
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Admin — MemberAddress
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(MemberAddress)
class MemberAddressAdmin(admin.ModelAdmin):
    list_display    = ("member", "full_address", "city", "state", "cep", "principal")
    list_filter     = ("state", "principal")
    search_fields   = ("member__user__first_name", "member__user__last_name", "road", "city", "cep")
    ordering        = ("member__user__first_name", "city")
    list_per_page   = 30
    readonly_fields = ("slug",)

    fieldsets = (
        (
            "Membro",
            {"fields": ("member", "principal")},
        ),
        (
            "Endereço",
            {
                "fields": (
                    "cep",
                    ("road", "number"),
                    ("district", "city", "state"),
                    "complement",
                    "country",
                    "slug",
                ),
            },
        ),
    )

    @admin.display(description="Endereço completo")
    def full_address(self, obj):
        return str(obj)


# ═══════════════════════════════════════════════════════════════════════════════
# Admin — MemberChurch
# ═══════════════════════════════════════════════════════════════════════════════

def activate_memberships(modeladmin, request, queryset):
    updated = queryset.update(status=MemberChurch.Status.ACTIVE)
    modeladmin.message_user(request, f"{updated} vínculo(s) ativado(s).", messages.SUCCESS)

activate_memberships.short_description = "✅ Ativar vínculos selecionados"


def deactivate_memberships(modeladmin, request, queryset):
    updated = queryset.update(
        status=MemberChurch.Status.INACTIVE,
        left_at=timezone.now(),
    )
    modeladmin.message_user(request, f"{updated} vínculo(s) desativado(s).", messages.WARNING)

deactivate_memberships.short_description = "🚫 Desativar vínculos selecionados"


@admin.register(MemberChurch)
class MemberChurchAdmin(admin.ModelAdmin):
    list_display = (
        "member_name",
        "church_name",
        "status_badge",
        "joined_at",
        "left_at",
        "duration",
    )
    list_filter         = ("status", "church")
    search_fields       = (
        "member__user__first_name",
        "member__user__last_name",
        "member__user__email",
        "church__user__first_name",
        "church__user__last_name",
    )
    autocomplete_fields = ("member", "church")
    ordering            = ("-joined_at",)
    date_hierarchy      = "joined_at"
    list_per_page       = 30
    save_on_top         = True
    actions             = [activate_memberships, deactivate_memberships, export_to_csv]
    readonly_fields     = ("joined_at",)

    fieldsets = (
        (
            "Vínculo",
            {
                "fields": (
                    ("member", "church"),
                    ("status", "joined_at"),
                    "left_at",
                ),
            },
        ),
    )

    # ── Colunas personalizadas ───────────────────────────────────────────────
    @admin.display(description="Membro", ordering="member__user__first_name")
    def member_name(self, obj):
        return obj.member.user.get_full_name()

    @admin.display(description="Igreja", ordering="church__user__first_name")
    def church_name(self, obj):
        return obj.church.user.get_full_name()

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        palette = {
            MemberChurch.Status.ACTIVE:   ("#065f46", "#d1fae5", "Ativo"),
            MemberChurch.Status.INACTIVE: ("#92400e", "#fef3c7", "Inativo"),
            MemberChurch.Status.PENDING:  ("#1e40af", "#dbeafe", "Pendente"),
        }
        fg, bg, label = palette.get(obj.status, ("#374151", "#f3f4f6", obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description="Duração")
    def duration(self, obj):
        end   = obj.left_at or timezone.now()
        delta = end - obj.joined_at
        days  = delta.days
        if days < 30:
            return f"{days} dia(s)"
        if days < 365:
            return f"{days // 30} mês/meses"
        return f"{days // 365} ano(s)"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("member__user", "church__user")
        )