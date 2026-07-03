import uuid
from datetime import datetime
from typing import Optional, Literal

from ninja import Schema, Field
from ecclesia.apps.community.models.church_in_church_model import ChurchAffiliationRequest
from ecclesia.apps.users.schemas.church_schemas import ChurchOut


# ============================================================
# SAÍDA COMPLETA
# ============================================================

class ChurchAffiliationRequestOut(Schema):
    id: uuid.UUID
    from_church: ChurchOut
    to_church: Optional[ChurchOut]
    invited_email: Optional[str]
    invited_church_full_name: Optional[str]
    request_type: ChurchAffiliationRequest.RequestType
    request_type_label: str
    status: ChurchAffiliationRequest.Status
    status_label: str
    code: Optional[str] = None  
    message: Optional[str] = None  
    created_at: datetime
    accepted_at: Optional[datetime] = None
    mode: ChurchAffiliationRequest.Mode
    mode_label: str
    expires_at: Optional[datetime] = None

    @classmethod
    def from_orm(cls, church_affiliation_request: ChurchAffiliationRequest) -> "ChurchAffiliationRequestOut":
        return cls(
            id=church_affiliation_request.id,
            from_church=ChurchOut.from_orm(church_affiliation_request.from_church),
            to_church=(ChurchOut.from_orm(church_affiliation_request.to_church)if church_affiliation_request.to_church else None),
            invited_email=church_affiliation_request.invited_email,
            invited_church_full_name=church_affiliation_request.invited_church_full_name,
            request_type=church_affiliation_request.request_type,
            request_type_label=church_affiliation_request.get_request_type_display(),
            status=church_affiliation_request.status,
            status_label=church_affiliation_request.get_status_display(),
            code=church_affiliation_request.code,
            message=church_affiliation_request.message,
            created_at=church_affiliation_request.created_at,
            accepted_at=church_affiliation_request.accepted_at,
            mode_label=church_affiliation_request.get_mode_display(),
            mode=church_affiliation_request.mode,
            expires_at=church_affiliation_request.expires_at,
        )


# ============================================================
# SEDE → IGREJA CADASTRADA - (ONLINE)
# ============================================================
class ChurchAffiliationInviteIn(Schema):
    message: Optional[str] = Field(None, max_length=500)
   

# ============================================================
# SEDE → IGREJA NÃO CADASTRADA - (OFFLINE)
# ============================================================

class ChurchAffiliationOfflineInviteIn(Schema):
    invited_email:str
    invited_church_full_name: str
    message: Optional[str] = Field(None, max_length=500)


# ============================================================
# COMUNIDADE → SEDE (ONLINE)
# ============================================================
class ChurchAffiliationRequestIn(Schema):
    message: Optional[str] = Field(None, max_length=500)
    

# ============================================================
# UPDATE
# ============================================================

class ChurchAffiliationRequestUpdate(Schema):
    status: ChurchAffiliationRequest.Status = Field(default=ChurchAffiliationRequest.Status.PENDING)
    message: Optional[str] = Field(None, max_length=500)
    

# ============================================================
# LISTAGEM
# ============================================================

class ChurchAffiliationRequestListOut(Schema):
    id: uuid.UUID
    from_church: str
    to_church: Optional[str]
    invited_email: Optional[str]
    invited_church_full_name: Optional[str]
    request_type_label: str
    request_type: ChurchAffiliationRequest.RequestType
    status: ChurchAffiliationRequest.Status
    status_label: str
    mode_label: str
    mode: ChurchAffiliationRequest.Mode
    created_at: datetime
    accepted_at: Optional[datetime]
    expires_at: Optional[datetime]  # ← era str, deve ser datetime

    @classmethod
    def from_orm(cls, church_affiliation_request: ChurchAffiliationRequest) -> "ChurchAffiliationRequestListOut":
        return cls(
            id=church_affiliation_request.id,
            from_church=church_affiliation_request.from_church.full_name or str(church_affiliation_request.from_church.id),
            to_church=(
                church_affiliation_request.to_church.full_name
                if church_affiliation_request.to_church
                else church_affiliation_request.invited_church_full_name
            ),
            request_type=church_affiliation_request.request_type,
            request_type_label=church_affiliation_request.get_request_type_display(),
            mode=church_affiliation_request.mode,
            mode_label=church_affiliation_request.get_mode_display(),
            status=church_affiliation_request.status,
            status_label=church_affiliation_request.get_status_display(),
            created_at=church_affiliation_request.created_at,
            accepted_at=church_affiliation_request.accepted_at,
            expires_at=church_affiliation_request.expires_at,
            invited_email=church_affiliation_request.invited_email,
            invited_church_full_name=church_affiliation_request.invited_church_full_name,
        )


# ============================================================
# FILTROS
# ============================================================

class ChurchAffiliationRequestFilter(Schema):
    status: Optional[list[ChurchAffiliationRequest.Status]] = None
    request_type: Optional[list[ChurchAffiliationRequest.RequestType]] = None

    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    church_id: Optional[uuid.UUID] = None
   

# ============================================================
# AÇÕES
# ============================================================

class ChurchAffiliationRequestAction(Schema):
    action: str = Field(..., pattern="^(accept|reject|cancel)$")  
    message: Optional[str] = None


# ============================================================
# CONSULTA POR CÓDIGO
# ============================================================

class ChurchAffiliationCodeLookupIn(Schema):
    code: str


# ============================================================
# RESPOSTA DO CONVITE OFFLINE
# ============================================================

class ChurchAffiliationOfflineInviteOut(Schema):
    id: uuid.UUID
    code: str
    invited_email: str
    invited_church_full_name: str
    created_at: datetime
    invite_url: str


# ============================================================
# ACEITAR CONVITE OFFLINE — INPUT
# ============================================================

class ChurchAffiliationOfflineAcceptIn(Schema):
    code: str


# ============================================================
# ACEITAR CONVITE OFFLINE — OUTPUT (EXISTENTE, mantido)
# ============================================================

class ChurchAffiliationOfflineAcceptOut(Schema):
    success: bool
    church_name: str
    email: str
    message: str
    affiliation_id: uuid.UUID


# ============================================================
# LOOKUP DO CONVITE OFFLINE — dados da tela pública  ← NOVO
# ============================================================

class ChurchAffiliationOfflineLookupOut(Schema):
    """
    Exibido na tela pública quando a igreja anônima acessa o link do e-mail.
    Mostra os dados da sede para que a igreja decida se aceita ou não.
    """
    id: uuid.UUID
    from_church_name: str
    from_church_type: str
    from_church_email: Optional[str]
    from_church_phone: Optional[str]
    from_church_website: Optional[str]
    from_church_instagram: Optional[str]
    from_church_about: Optional[str]
    from_church_banner: Optional[str]
    invited_church_full_name: str
    invited_email: str
    message: Optional[str]
    expires_at: Optional[datetime]
    is_expired: bool

    @classmethod
    def from_orm(cls, obj: ChurchAffiliationRequest) -> "ChurchAffiliationOfflineLookupOut":
        return cls(
            id=obj.id,
            from_church_name=obj.from_church.full_name or "",
            from_church_type=obj.from_church.get_church_type_display(),
            from_church_email=obj.from_church.user.email,
            from_church_phone=str(obj.from_church.phone) if obj.from_church.phone else None,
            from_church_website=obj.from_church.website,
            from_church_instagram=obj.from_church.instagram,
            from_church_about=obj.from_church.about,
            from_church_banner=obj.from_church.banner_url,
            invited_church_full_name=obj.invited_church_full_name or "",
            invited_email=obj.invited_email or "",
            message=obj.message,
            expires_at=obj.expires_at,
            is_expired=obj.is_expired(),
        )


# ============================================================
# ACEITE COM JWT — retorno após criação da conta  ← NOVO
# ============================================================

class ChurchAffiliationOfflineAcceptWithTokensOut(Schema):
    """
    Retornado após a nova igreja aceitar o convite e ter a conta criada.
    Contém tokens JWT para login automático + dados da afiliação.
    """
    access: str
    refresh: str
    affiliation_id: uuid.UUID
    church_full_name: Optional[str] = None
    from_church_name: Optional[str] = None
    is_new: bool = True


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "ChurchAffiliationRequestOut",
    "ChurchAffiliationInviteIn",
    "ChurchAffiliationOfflineInviteIn",
    "ChurchAffiliationRequestIn",
    "ChurchAffiliationRequestUpdate",
    "ChurchAffiliationRequestListOut",
    "ChurchAffiliationRequestFilter",
    "ChurchAffiliationRequestAction",
    "ChurchAffiliationCodeLookupIn",
    "ChurchAffiliationOfflineInviteOut",
    "ChurchAffiliationOfflineAcceptIn",
    "ChurchAffiliationOfflineAcceptOut",
    "ChurchAffiliationOfflineLookupOut",
    "ChurchAffiliationOfflineAcceptWithTokensOut",
]