"""
Church Members router — Igreja cadastra e lista seus membros.
Pertence ao app community.
"""
import uuid
from ninja import Router, Query
from django_ratelimit.decorators import ratelimit
from django.core.exceptions import ValidationError
from ecclesia.apps.users.models.church import Church
from ecclesia.apps.users.permissions import ChurchOnlyAuth
from ecclesia.apps.users.exceptions import UserAlreadyExists
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

)
from ecclesia.apps.community.services.church_in_church_service import (
    create_affiliation_request,
    create_offline_invite,
    create_authenticated_invite,
)

router = Router(tags=["Churches"])




# ============================================================
# SEDE → IGREJA CADASTRADA (ONLINE) - ENVIAR CONVITE
# ============================================================
@router.post("/church/affiliation/invite/{to_church_id}",
    auth=ChurchOnlyAuth(),
    response={201: ChurchAffiliationRequestOut, 409: MessageOut},
    summary="Igreja Sede/Matriz envia convite de afiliação",
    description=(
        "Uma igreja do tipo Sede/Matriz pode enviar um convite de afiliação "
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
    summary="Igreja Sede/Matriz envia convite offline",
    description=(
        "Uma igreja do tipo Sede/Matriz pode enviar um convite offline "
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

    # Retorna com URL de aceite
    invite_url = f"{request.build_absolute_uri('/')}api/community/church/affiliation/offline-accept?code={church_affiliation.code}"
    
    return 201, ChurchAffiliationOfflineInviteOut(
        id=church_affiliation.id,
        code=church_affiliation.code,
        invited_email=church_affiliation.invited_email,
        invited_church_full_name=church_affiliation.invited_church_full_name,
        created_at=church_affiliation.created_at,
        invite_url=invite_url,
    )


# ============================================================
# COMUNIDADE → SEDE (ONLINE) - SOLICITAR AFILIAÇÃO
# ============================================================
@router.post(
    "/church/affiliation/request",
    auth=ChurchOnlyAuth(),
    response={201: ChurchAffiliationRequestOut, 409: MessageOut},
    summary="Igreja Comunidade solicita afiliação a uma Sede/Matriz",
    description=(
        "Uma igreja do tipo Comunidade pode solicitar afiliação "
        "a uma igreja do tipo Sede/Matriz. A solicitação fica pendente "
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
            message=payload.message
        )
    except ValidationError as e:
        return 409, {"detail": str(e)}

    return 201, ChurchAffiliationRequestOut.from_orm(church_affiliation)


# # ============================================================
# # ACEITAR/REJEITAR/CANCELAR SOLICITAÇÃO/CONVITE
# # ============================================================
# @router.patch(
#     "/church/affiliation/{affiliation_id}",
#     auth=ChurchOnlyAuth(),
#     response={200: ChurchAffiliationRequestOut, 404: MessageOut, 409: MessageOut},
#     summary="Aceitar, rejeitar ou cancelar solicitação/convite",
#     description=(
#         "Aceitar: A igreja destino aceita o convite ou solicitação.\n"
#         "Rejeitar: A igreja destino rejeita o convite ou solicitação.\n"
#         "Cancelar: A igreja origem cancela o convite ou solicitação."
#     ),
# )
# @ratelimit(key="user", rate="30/m", block=True)
# def handle_affiliation_action(
#     request,
#     affiliation_id: uuid.UUID,
#     payload: ChurchAffiliationRequestAction,
# ):
#     church = request.auth.church
    
#     # Busca a solicitação
#     affiliation = ChurchAffiliationRequest.objects.filter(id=affiliation_id).first()
#     if not affiliation:
#         return 404, {"detail": "Solicitação não encontrada."}
    
#     # Verifica permissão
#     if payload.action == "accept" or payload.action == "reject":
#         # Apenas a igreja destino pode aceitar/rejeitar
#         if affiliation.to_church_id != church.id:
#             return 409, {"detail": "Você não tem permissão para esta ação."}
#     elif payload.action == "cancel":
#         # Apenas a igreja origem pode cancelar
#         if affiliation.from_church_id != church.id:
#             return 409, {"detail": "Você não tem permissão para esta ação."}
#     else:
#         return 409, {"detail": f"Ação inválida: {payload.action}"}
    
#     try:
#         if payload.action == "accept":
#             affiliation.accept()
#         elif payload.action == "reject":
#             affiliation.reject()
#         elif payload.action == "cancel":
#             affiliation.cancel()
#     except ValidationError as e:
#         return 409, {"detail": str(e)}
    
#     return 200, ChurchAffiliationRequestOut.from_orm(affiliation)


# # ============================================================
# # ACEITAR CONVITE OFFLINE POR CÓDIGO
# # ============================================================
# @router.post(
#     "/church/affiliation/offline-accept",
#     response={200: ChurchAffiliationOfflineAcceptOut, 404: MessageOut, 409: MessageOut},
#     summary="Aceitar convite offline por código",
#     description=(
#         "Uma igreja não cadastrada pode aceitar um convite offline "
#         "informando o código recebido por email."
#     ),
#     auth=None,  # ✅ Não requer autenticação
# )
# def accept_offline_invite(
#     request,
#     payload: ChurchAffiliationCodeLookupIn,
# ):
#     try:
#         affiliation = validate_offline_invite_code(payload.code)
#         if not affiliation:
#             return 404, {"detail": "Código inválido ou expirado."}
        
#         # Aceita o convite offline
#         affiliation.accept()
        
#         # Retorna informações para criar a igreja
#         return 200, ChurchAffiliationOfflineAcceptOut(
#             success=True,
#             church_name=affiliation.invited_church_full_name,
#             email=affiliation.invited_email,
#             message="Convite aceito com sucesso! Crie sua igreja agora.",
#             affiliation_id=affiliation.id,
#         )
#     except ValidationError as e:
#         return 409, {"detail": str(e)}


# # ============================================================
# # LISTAR SOLICITAÇÕES/CONVITES DA IGREJA
# # ============================================================
# @router.get(
#     "/church/affiliations",
#     auth=ChurchOnlyAuth(),
#     response={200: list[ChurchAffiliationRequestListOut]},
#     summary="Listar todas as solicitações/convites da igreja",
# )
# @ratelimit(key="user", rate="60/m", block=True)
# def list_church_affiliations(
#     request,
#     status: Optional[str] = None,
#     request_type: Optional[str] = None,
# ):
#     church = request.auth.church
    
#     queryset = ChurchAffiliationRequest.objects.filter(
#         Q(from_church_id=church.id) | Q(to_church_id=church.id)
#     ).select_related("from_church", "to_church")
    
#     if status:
#         queryset = queryset.filter(status=status)
    
#     if request_type:
#         queryset = queryset.filter(request_type=request_type)
    
#     affiliations = queryset.order_by("-created_at")
    
#     return 200, [ChurchAffiliationRequestListOut.from_orm(a) for a in affiliations]


# # ============================================================
# # BUSCAR SOLICITAÇÃO/CONVITE POR ID
# # ============================================================
# @router.get(
#     "/church/affiliation/{affiliation_id}",
#     auth=ChurchOnlyAuth(),
#     response={200: ChurchAffiliationRequestOut, 404: MessageOut},
#     summary="Buscar solicitação/convite por ID",
# )
# @ratelimit(key="user", rate="60/m", block=True)
# def get_church_affiliation(
#     request,
#     affiliation_id: uuid.UUID,
# ):
#     church = request.auth.church
    
#     affiliation = ChurchAffiliationRequest.objects.filter(
#         Q(from_church_id=church.id) | Q(to_church_id=church.id),
#         id=affiliation_id,
#     ).select_related("from_church", "to_church").first()
    
#     if not affiliation:
#         return 404, {"detail": "Solicitação não encontrada."}
    
#     return 200, ChurchAffiliationRequestOut.from_orm(affiliation)