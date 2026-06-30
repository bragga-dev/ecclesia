"""
MemberChurch Admin — configuração do Django Admin para MemberChurch.
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.admin.actions import  export_to_csv
from ecclesia.apps.community.admin.actions import activate_memberships, deactivate_memberships


@admin.register(MemberChurch)
class MemberChurchAdmin(admin.ModelAdmin):
    list_display = (
        "member_name",
        "church_name",
        "role_badge",
        "status_badge",
        "joined_at",
        "left_at",
        "duration",
    )
    list_filter = ("status", "church", "role")  
    search_fields = (
        "member__user__first_name",
        "member__user__last_name",
        "member__user__email",
        "church__user__first_name",
        "church__user__last_name",
    )
    autocomplete_fields = ("member", "church")
    ordering = ("-joined_at",)
    date_hierarchy = "joined_at"
    list_per_page = 30
    save_on_top = True
    actions = [activate_memberships, deactivate_memberships, export_to_csv]
    readonly_fields = ("joined_at",)

    fieldsets = (
        (
            "Vínculo",
            {
                "fields": (
                    ("member", "church"),
                    ("role", "status"),
                    "joined_at",
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

    @admin.display(description="Função", ordering="role")
    def role_badge(self, obj):
        palette = {
            MemberChurch.Role.MEMBER: ("#374151", "#f3f4f6", "👤 Membro"),
            MemberChurch.Role.PASTOR: ("#065f46", "#d1fae5", "⛪ Pastor/Padre"),
            MemberChurch.Role.TREASURER: ("#92400e", "#fef3c7", "💰 Tesoureiro"),
            MemberChurch.Role.SECRETARY: ("#1e40af", "#dbeafe", "📋 Secretário"),
            MemberChurch.Role.CHURCH_ADMIN: ("#7c3aed", "#ede9fe", "⚙️ Administrador"),
        }
        fg, bg, label = palette.get(obj.role, ("#374151", "#f3f4f6", obj.role))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        palette = {
            MemberChurch.Status.ACTIVE: ("#065f46", "#d1fae5", "✅ Ativo"),
            MemberChurch.Status.INACTIVE: ("#92400e", "#fef3c7", "🚫 Inativo"),
            MemberChurch.Status.PENDING: ("#1e40af", "#dbeafe", "⏳ Pendente"),
        }
        fg, bg, label = palette.get(obj.status, ("#374151", "#f3f4f6", obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, label,
        )

    @admin.display(description="Duração")
    def duration(self, obj):
        end = obj.left_at or timezone.now()
        delta = end - obj.joined_at
        days = delta.days
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