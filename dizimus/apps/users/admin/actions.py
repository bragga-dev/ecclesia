"""
Admin Actions — ações globais reutilizáveis.
"""
import csv
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ..models import User, MemberChurch


def export_to_csv(modeladmin, request, queryset):
    """Ação genérica: exporta os campos list_display do queryset para CSV."""
    meta = modeladmin.model._meta
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


def activate_memberships(modeladmin, request, queryset):
    updated = queryset.update(status=MemberChurch.Status.ACTIVE)
    modeladmin.message_user(request, f"{updated} vínculo(s) ativado(s).", messages.SUCCESS)
activate_memberships.short_description = "✅ Ativar vínculos selecionados"


def deactivate_memberships(modeladmin, request, queryset):
    from django.utils import timezone
    updated = queryset.update(
        status=MemberChurch.Status.INACTIVE,
        left_at=timezone.now(),
    )
    modeladmin.message_user(request, f"{updated} vínculo(s) desativado(s).", messages.WARNING)
deactivate_memberships.short_description = "🚫 Desativar vínculos selecionados"