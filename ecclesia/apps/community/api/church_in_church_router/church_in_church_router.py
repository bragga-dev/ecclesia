"""
Church Members router — Igreja cadastra e lista seus membros.
Pertence ao app community.
"""
import uuid
from ecclesia.apps.community.selectors.church_in_church_selector import get_offline_invites_by_code
from django.conf import settings
from ninja import Router, Query
from django_ratelimit.decorators import ratelimit
from django.core.exceptions import ValidationError
from ecclesia.apps.users.permissions import ChurchOnlyAuth
from ecclesia.apps.users.schemas.users_schemas import MessageOut
from ecclesia.apps.users.utils.pagination import paginate_queryset, PageOut
from ecclesia.apps.community.schemas.church_in_church_schema import (
    ChurchAffiliationInviteIn,
    ChurchAffiliationRequestListOut,
    ChurchAffiliationRequestOut,
    ChurchAffiliationRequestIn,
    ChurchAffiliationOfflineInviteOut,
    ChurchAffiliationOfflineInviteIn,
    ChurchAffiliationRequestAction,
    ChurchAffiliationCodeLookupIn,
    ChurchAffiliationOfflineLookupOut,
    ChurchAffiliationOfflineAcceptIn,
    ChurchAffiliationOfflineAcceptOut,
    ChurchAffiliationOfflineAcceptWithTokensOut,

)
from ecclesia.apps.community.services.church_in_church_service import (
    create_affiliation_request,
    create_offline_invite,
    create_authenticated_invite,
    accept_offline_invite,
    get_pending_offline_invites,
    handle_affiliation_action,
    get_pending_offline_invites,
    

)

router = Router(tags=["Churches"])




# ============================================================
# SEDE → IGREJA CADASTRADA (ONLINE) - ENVIAR CONVITE
# ============================================================
@router.post("/church/affiliation/invite/{to_church_id}",
    auth=ChurchOnlyAuth(),
    response={201: ChurchAffiliationRequestOut, 409: MessageOut},
    summary="Igreja Paróquia envia convite de afiliação",
    description=(
        "Uma igreja do tipo Paróquia pode enviar um convite de afiliação "
        "para uma igreja do tipo Comunidade. O convite fica pendente até que "
        "a igreja convidada o aceite ou rejeite."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def create_church_affiliation_invite(request, payload: ChurchAffiliationInviteIn, to_church_id: uuid.UUID):
    from_church_id = request.auth.church.id    
    try:
        church_affiliation = create_authenticated_invite(from_church_id=from_church_id, to_church_id=to_church_id, message=payload.message)
    except ValidationError as e:
        return 409, {"detail": str(e)}

    return 201, ChurchAffiliationRequestOut.from_orm(church_affiliation)


# ============================================================
# SEDE → IGREJA NÃO CADASTRADA (OFFLINE) - ENVIAR CONVITE
# ============================================================
@router.post(
    "/church/affiliation/offline-invite",
    auth=ChurchOnlyAuth(),
    response={201: ChurchAffiliationOfflineInviteOut, 409: MessageOut},
    summary="Igreja Paróquia envia convite offline",
    description=(
        "Uma igreja do tipo Paróquia pode enviar um convite offline "
        "para uma igreja que ainda não está cadastrada no sistema."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def create_church_offline_invite(
    request, 
    payload: ChurchAffiliationOfflineInviteIn,
):
    from_church = request.auth.church
    
    try:
        church_affiliation = create_offline_invite(
            from_church=from_church,
            invited_email=payload.invited_email,
            invited_church_full_name=payload.invited_church_full_name,
            message=payload.message,
        )
    except ValidationError as e:
        return 409, {"detail": str(e)}

    invite_url = f"{settings.FRONTEND_URL}/dashboard/community/affiliations/{church_affiliation.code}"
    
    return 201, ChurchAffiliationOfflineInviteOut(
        id=church_affiliation.id,
        code=church_affiliation.code,
        invited_email=church_affiliation.invited_email,
        invited_church_full_name=church_affiliation.invited_church_full_name,
        created_at=church_affiliation.created_at,
        invite_url=invite_url,
    )

# ============================================================
# CONSULTA DO CONVITE OFFLINE (público — sem auth)
# ============================================================
@router.get(
    "/church/affiliation/offline/lookup",
    auth=None,
    response={200: ChurchAffiliationOfflineLookupOut, 404: MessageOut, 410: MessageOut},
    summary="Consulta convite offline por código",
    description=(
        "Rota pública. Recebe o code da URL do e-mail e retorna os dados "
        "do convite para exibição na tela de boas-vindas."
    ),
)
def lookup_offline_invite_endpoint(request, code: str):
    try:
        invite = get_pending_offline_invites(code=code)
    except ValidationError as e:
        return 404, {"detail": str(e)}

    if invite is None:
        return 404, {"detail": "Convite não encontrado"}

    out = ChurchAffiliationOfflineLookupOut.from_orm(invite)

    if out.is_expired:
        return 410, {"detail": "Este convite expirou. Solicite um novo à igreja remetente."}

    return 200, out

# ============================================================
# ACEITE DO CONVITE OFFLINE (público — sem auth)
# ============================================================
@router.post(
    "/church/affiliation/offline/accept",
    auth=None,
    response={200: ChurchAffiliationOfflineAcceptWithTokensOut, 400: MessageOut, 404: MessageOut},
    summary="Igreja anônima aceita o convite e recebe tokens JWT",
    description=(
        "Rota pública. A conta já existe (criada pela task no envio). "
        "Este endpoint confirma o aceite e retorna tokens para login automático."
    ),
)
@ratelimit(key="ip", rate="20/h", block=True)
def accept_offline_invite_endpoint(request, code: str):
    try:
        result = accept_offline_invite(code=code)
    except ValidationError as e:
        msg = str(e)
        status = 404 if "não encontrado" in msg else 400
        return status, {"detail": msg}

    return 200, ChurchAffiliationOfflineAcceptWithTokensOut(**result)


# ============================================================
# AÇÃO EM CONVITE/SOLICITAÇÃO (autenticado — Igreja)
# ============================================================
@router.patch(
    "/church/affiliation/{affiliation_id}/action",
    auth=ChurchOnlyAuth(),
    response={200: ChurchAffiliationRequestOut, 403: MessageOut, 404: MessageOut, 409: MessageOut},
    summary="Aceitar, rejeitar ou cancelar solicitação/convite",
    description=(
        "accept/reject: apenas a igreja destinatária.\n"
        "cancel: apenas a igreja remetente."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def handle_affiliation_action_endpoint(
    request,
    affiliation_id: uuid.UUID,
    payload: ChurchAffiliationRequestAction,
):
    church = request.auth.church

    try:
        affiliation = handle_affiliation_action(
            affiliation_id=affiliation_id,
            church=church,
            action=payload.action,
        )
    except ValidationError as e:
        msg = str(e)
        if "não encontrada" in msg:
            return 404, {"detail": msg}
        return 409, {"detail": msg}
    except PermissionError as e:
        return 403, {"detail": str(e)}

    return 200, ChurchAffiliationRequestOut.from_orm(affiliation)

# ============================================================
# COMUNIDADE → SEDE (ONLINE) - SOLICITAR AFILIAÇÃO
# ============================================================
@router.post(
    "/church/affiliation/request",
    auth=ChurchOnlyAuth(),
    response={201: ChurchAffiliationRequestOut, 409: MessageOut},
    summary="Igreja Comunidade solicita afiliação a uma Paróquia",
    description=(
        "Uma igreja do tipo Comunidade pode solicitar afiliação "
        "a uma igreja do tipo Paróquia. A solicitação fica pendente "
        "até que a sede aceite ou rejeite."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def create_church_affiliation_request(request,  payload: ChurchAffiliationRequestIn, to_church_id: uuid.UUID,):
    from_church_id = request.auth.church.id
    
    try:
        church_affiliation = create_affiliation_request(
            from_church_id=from_church_id,
            to_church_id=to_church_id,
            message=payload.message,
        )
    except ValidationError as e:
        return 409, {"detail": str(e)}

    return 201, ChurchAffiliationRequestOut.from_orm(church_affiliation)

