"""
Admin Actions — ações globais reutilizáveis.
"""
import csv
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from dizimus.apps.users.models.user import User


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
    writer.writerow([
        "Nome completo",
        "Nome de usuário",
        "E-mail",
        "CPF",
        "Data de nascimento",
        "Telefone",
        "Igrejas vinculadas",
    ])
    for m in queryset.select_related("user").prefetch_related("church_memberships"):
        writer.writerow([
            m.get_full_name(),
            m.username or "—",
            m.user.email,
            m.cpf or "—",
            m.date_of_birth.strftime("%d/%m/%Y") if m.date_of_birth else "—",
            str(m.phone) if m.phone else "—",
            m.church_memberships.count(),
        ])
    return response
export_members_csv.short_description = "⬇ Exportar membros selecionados para CSV"


def export_churches_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="igrejas.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Nome",
        "CNPJ",
        "Tipo",
        "Verificada",
        "Total de membros",
        "Telefone",
        "Instagram",
        "Website",
        "E-mail",
        "Igreja pai",
    ])
    for c in queryset.select_related("user", "parent_church"):
        writer.writerow([
            c.full_name or "—",
            c.cnpj or "—",
            c.get_church_type_display(),
            "Sim" if c.is_verified else "Não",
            c.total_members,
            str(c.phone) if c.phone else "—",
            c.instagram or "—",
            c.website or "—",
            c.user.email,
            c.parent_church.full_name if c.parent_church else "—",
        ])
    return response
export_churches_csv.short_description = "⬇ Exportar igrejas selecionadas para CSV"