

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from dizimus.apps.community.models.member_church_model import MemberChurch



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