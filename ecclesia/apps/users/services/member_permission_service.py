"""
Service de permissões de membros em igrejas.
"""
import uuid
from typing import Optional
from datetime import datetime

from django.core.exceptions import ValidationError

from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.member_church_permission import MemberChurchPermission
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.selectors.member_permission_selector import (
    get_member_church,
    get_member_permission_by_id,
    get_system_permission_by_code,
)


def grant_permission(
    *,
    member_id: uuid.UUID,
    church_id: uuid.UUID,
    permission_code: str,
    granted_by: User,
    expires_at: Optional[datetime] = None,
) -> MemberChurchPermission:
    """
    Atribui uma permissão a um membro em uma igreja.

    Regras:
    - O membro deve ter vínculo ativo na igreja
    - A permissão deve existir e estar ativa no sistema
    - Não pode duplicar uma permissão já existente (mesmo inativa)
    """
    member_church = get_member_church(member_id=member_id, church_id=church_id)
    if not member_church:
        raise ValidationError(
            "Membro não encontrado ou sem vínculo ativo nesta igreja."
        )

    system_permission = get_system_permission_by_code(permission_code)
    if not system_permission:
        raise ValidationError(
            f"Permissão '{permission_code}' não encontrada ou inativa."
        )

    # Verifica duplicata
    existing = MemberChurchPermission.objects.filter(
        member_church=member_church,
        permission=system_permission,
    ).first()

    if existing:
        if existing.is_active:
            raise ValidationError(
                f"O membro já possui a permissão '{permission_code}'."
            )
        # Reativa se existir inativa
        existing.is_active = True
        existing.expires_at = expires_at
        existing.granted_by = granted_by
        existing.save(update_fields=["is_active", "expires_at", "granted_by"])
        return existing

    return MemberChurchPermission.objects.create(
        member_church=member_church,
        permission=system_permission,
        granted_by=granted_by,
        expires_at=expires_at,
    )


def update_permission(
    *,
    permission_id: uuid.UUID,
    member_id: uuid.UUID,
    church_id: uuid.UUID,
    is_active: Optional[bool] = None,
    expires_at: Optional[datetime] = None,
) -> MemberChurchPermission:
    """Atualiza is_active ou expires_at de uma permissão."""
    member_church = get_member_church(member_id=member_id, church_id=church_id)
    if not member_church:
        raise ValidationError(
            "Membro não encontrado ou sem vínculo ativo nesta igreja."
        )

    permission = get_member_permission_by_id(
        permission_id=permission_id,
        member_church=member_church,
    )
    if not permission:
        raise ValidationError("Permissão não encontrada.")

    update_fields = []

    if is_active is not None:
        permission.is_active = is_active
        update_fields.append("is_active")

    if expires_at is not None:
        permission.expires_at = expires_at
        update_fields.append("expires_at")

    if update_fields:
        permission.save(update_fields=update_fields)

    return permission


def revoke_permission(
    *,
    permission_id: uuid.UUID,
    member_id: uuid.UUID,
    church_id: uuid.UUID,
) -> None:
    """Remove permanentemente uma permissão de um membro."""
    member_church = get_member_church(member_id=member_id, church_id=church_id)
    if not member_church:
        raise ValidationError(
            "Membro não encontrado ou sem vínculo ativo nesta igreja."
        )

    permission = get_member_permission_by_id(
        permission_id=permission_id,
        member_church=member_church,
    )
    if not permission:
        raise ValidationError("Permissão não encontrada.")

    permission.delete()