import uuid
from datetime import datetime
from typing import Optional, Literal

from ninja import Schema, Field

from dizimus.apps.community.models.church_in_church_model import ChurchAffiliationRequest
from dizimus.apps.users.schemas.church_schemas import ChurchOut


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
        )


# ============================================================
# SEDE → IGREJA CADASTRADA
# ============================================================
class ChurchAffiliationInviteIn(Schema):
    status: ChurchAffiliationRequest.Status = Field(default=ChurchAffiliationRequest.Status.PENDING)
    request_type: Literal[ChurchAffiliationRequest.RequestType.INVITE]
    mode: Literal[ChurchAffiliationRequest.Mode.AUTHENTICATED]
    message: Optional[str] = Field(None, max_length=500)
   

# ============================================================
# SEDE → IGREJA NÃO CADASTRADA
# ============================================================

class ChurchAffiliationOfflineInviteIn(Schema):
    invited_email:str
    invited_church_full_name: str
    code: str
    status: ChurchAffiliationRequest.Status = Field(default=ChurchAffiliationRequest.Status.PENDING)
    request_type: Literal[ChurchAffiliationRequest.RequestType.INVITE]
    mode: Literal[ChurchAffiliationRequest.Mode.OFFLINE]
    message: Optional[str] = Field(None, max_length=500)

# ============================================================
# COMUNIDADE → SEDE
# ============================================================
class ChurchAffiliationRequestIn(Schema):
    id: uuid.UUID
    from_church: ChurchOut
    to_church: ChurchOut
    status: ChurchAffiliationRequest.Status = Field(default=ChurchAffiliationRequest.Status.PENDING)
    request_type: Literal[ChurchAffiliationRequest.RequestType.REQUEST]
    mode: Literal[ChurchAffiliationRequest.Mode.AUTHENTICATED]
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
    from_church: ChurchOut
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

    @classmethod
    def from_orm(cls, church_affiliation_request: ChurchAffiliationRequest) -> "ChurchAffiliationRequestListOut":
        return cls(
            id=church_affiliation_request.id,
            from_church=church_affiliation_request.from_church.full_name or str(church_affiliation_request.from_church.id),
            to_church=church_affiliation_request.to_church.full_name or str(church_affiliation_request.to_church.id),
            request_type=church_affiliation_request.request_type,
            request_type_label=church_affiliation_request.get_request_type_display(),
            mode=church_affiliation_request.mode,
            mode_label=church_affiliation_request.get_mode_display(),
            status=church_affiliation_request.status,
            status_label=church_affiliation_request.get_status_display(),
            created_at=church_affiliation_request.created_at,
            accepted_at=church_affiliation_request.accepted_at,
        )


# ============================================================
# FILTROS
# ============================================================

class ChurchAffiliationRequestFilter(Schema):
    status: Optional[list[ChurchAffiliationRequest.Status]] = None
    request_type: Optional[list[ChurchAffiliationRequest.RequestType]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    query: Optional[str] = None  
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
# ACEITAR CONVITE OFFLINE
# ============================================================

class ChurchAffiliationOfflineAcceptIn(Schema):

    code: str


class ChurchAffiliationOfflineAcceptOut(Schema):

    success: bool

    church_name: str

    email: str

    message: str

    affiliation_id: uuid.UUID


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
]