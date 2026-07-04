"""
Selectors de permissões de membros em igrejas.
"""
import uuid
from typing import Optional
from django.db.models import QuerySet

from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.member_church_permission import MemberChurchPermission
from ecclesia.apps.users.models.system_permission import SystemPermission


def get_member_church(
    member_id: uuid.UUID,
    church_id: uuid.UUID,
) -> Optional[MemberChurch]:
    """Retorna o vínculo ativo de um membro em uma igreja."""
    return (
        MemberChurch.objects
        .select_related("member__user", "church")
        .filter(
            member_id=member_id,
            church_id=church_id,
            status=MemberChurch.Status.ACTIVE,
        )
        .first()
    )


def get_member_permissions(
    member_church: MemberChurch,
) -> QuerySet[MemberChurchPermission]:
    """Retorna todas as permissões de um MemberChurch."""
    return (
        MemberChurchPermission.objects
        .select_related("permission", "granted_by")
        .filter(member_church=member_church)
        .order_by("permission__module", "permission__code")
    )


def get_member_permission_by_id(
    permission_id: uuid.UUID,
    member_church: MemberChurch,
) -> Optional[MemberChurchPermission]:
    """Retorna uma permissão específica de um MemberChurch pelo id."""
    return (
        MemberChurchPermission.objects
        .select_related("permission", "granted_by")
        .filter(id=permission_id, member_church=member_church)
        .first()
    )


def get_system_permission_by_code(code: str) -> Optional[SystemPermission]:
    """Retorna uma SystemPermission pelo código."""
    return SystemPermission.objects.filter(code=code, is_active=True).first()


def get_all_system_permissions() -> QuerySet[SystemPermission]:
    """Retorna todas as permissões ativas do sistema."""
    return (
        SystemPermission.objects
        .filter(is_active=True)
        .order_by("module", "code")
    )