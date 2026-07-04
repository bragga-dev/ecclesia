"""
Schemas de permissões de membros em igrejas.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from ninja import Schema, Field


# ── Saída de SystemPermission ─────────────────────────────────────────────────

class SystemPermissionOut(Schema):
    id: uuid.UUID
    code: str
    name: str
    module: str
    description: Optional[str]
    is_active: bool


# ── Saída de MemberChurchPermission ──────────────────────────────────────────

class MemberPermissionOut(Schema):
    id: uuid.UUID
    permission_code: str
    permission_name: str
    permission_module: str
    is_active: bool
    is_effective: bool
    granted_at: datetime
    expires_at: Optional[datetime]
    granted_by_email: Optional[str]

    @classmethod
    def from_orm(cls, obj) -> "MemberPermissionOut":
        return cls(
            id=obj.id,
            permission_code=obj.permission.code,
            permission_name=obj.permission.name,
            permission_module=obj.permission.module,
            is_active=obj.is_active,
            is_effective=obj.is_effective,
            granted_at=obj.granted_at,
            expires_at=obj.expires_at,
            granted_by_email=obj.granted_by.email if obj.granted_by else None,
        )


# ── Input de atribuição ───────────────────────────────────────────────────────

class GrantPermissionIn(Schema):
    permission_code: str = Field(..., description="Código da permissão. Ex: members.view")
    expires_at: Optional[datetime] = Field(
        None,
        description="Data de expiração. Deixe em branco para permanente."
    )


# ── Input de atualização ──────────────────────────────────────────────────────

class UpdatePermissionIn(Schema):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None