"""
Church Members router — Igreja cadastra e lista seus membros.
Pertence ao app community.
"""
from ninja import Router, Query
from django_ratelimit.decorators import ratelimit
import uuid
from dizimus.apps.users.permissions import ChurchOnlyAuth
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.users.utils.pagination import paginate_queryset, PageOut
from dizimus.apps.community.models.member_church_model import MemberChurch
from dizimus.apps.users.schemas.member_schemas import MemberOut, MemberUpdateIn
from dizimus.apps.community.schemas.member_church_schema import (
    ChurchRegisterMemberIn,
    MemberInviteOut,
    ChurchMemberListOut,
    MemberChurchOut,
    MemberChurchUpdateIn,
)
from dizimus.apps.community.services.member_church_service import (
    register_member_by_church,
    list_member_church_service,
    update_member_church_service,
    delete_member_church_service,
    get_church_membership_service,
)
from dizimus.apps.users.services.profile import update_member_profile
from dizimus.apps.community.selectors.member_church_selector import get_member_church_by_id

router = Router(tags=["Churches"])


@router.post(
    "/members",
    auth=ChurchOnlyAuth(),
    response={201: MemberInviteOut, 409: MessageOut},
    summary="Igreja cadastra um membro",
    description=(
        "Apenas a Igreja autenticada pode cadastrar membros. "
        "O membro recebe um e-mail com senha temporária e link de verificação."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def church_register_member(request, payload: ChurchRegisterMemberIn):
    church = request.auth.church
    try:
        member = register_member_by_church(
            church=church,
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            role=payload.role,
            status=payload.status,
            contribution_type=payload.contribution_type,
        )
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}

    return 201, MemberInviteOut(
        id=member.user.id,
        email=member.user.email,
        first_name=member.first_name,
        last_name=member.last_name,
    )

# ________________________________________________________________

@router.get(
    "/members",
    auth=ChurchOnlyAuth(),
    response={200: PageOut[ChurchMemberListOut]},
    summary="Lista membros ativos",
    description="Retorna todos os membros com status ACTIVE vinculados à igreja autenticada.",
)
def church_list_members(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    memberships = list_member_church_service(
        church_id=request.auth.church.id,
    )
    return paginate_queryset(memberships, page, page_size, ChurchMemberListOut.from_membership)

#______________________________________________________________________________________________________

@router.get(
    "/members/all",
    auth=ChurchOnlyAuth(),
    response={200: PageOut[ChurchMemberListOut]},
    summary="Lista todos os vínculos",
    description="Retorna todos os membros independente de status.",
)
def church_list_all_members(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    memberships = list_member_church_service(
        church_id=request.auth.church.id,
        status=None,
    )
    return paginate_queryset(memberships, page, page_size, ChurchMemberListOut.from_membership)


@router.get(
    "/members/pending",
    auth=ChurchOnlyAuth(),
    response={200: PageOut[ChurchMemberListOut]},
    summary="Lista membros pendentes",
    description="Retorna membros com status PENDING aguardando aprovação.",
)
def church_list_pending_members(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    memberships = list_member_church_service(
        church_id=request.auth.church.id,
        status=MemberChurch.Status.PENDING,
    )
    return paginate_queryset(memberships, page, page_size, ChurchMemberListOut.from_membership)


@router.get(
    "/members/treasurers",
    auth=ChurchOnlyAuth(),
    response={200: PageOut[ChurchMemberListOut]},
    summary="Lista tesoureiros ativos",
    description="Retorna membros ativos com função de tesoureiro.",
)
def church_list_treasurers(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    memberships = list_member_church_service(
        church_id=request.auth.church.id,
        roles=[MemberChurch.Role.TREASURER],
    )
    return paginate_queryset(memberships, page, page_size, ChurchMemberListOut.from_membership)


@router.get(
    "/members/leaders",
    auth=ChurchOnlyAuth(),
    response={200: PageOut[ChurchMemberListOut]},
    summary="Lista liderança ativa",
    description="Retorna membros ativos com função de pastor, secretário ou admin.",
)
def church_list_leaders(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    memberships = list_member_church_service(
        church_id=request.auth.church.id,
        roles=[
            MemberChurch.Role.PASTOR,
            MemberChurch.Role.SECRETARY,
            MemberChurch.Role.CHURCH_ADMIN,
        ],
    )
    return paginate_queryset(memberships, page, page_size, ChurchMemberListOut.from_membership)


#___________________________________________________________________________________________________________

@router.patch(
    "/members/{membership_id}",
    auth=ChurchOnlyAuth(),
    response={201: MemberChurchOut, 404: MessageOut, 409: MessageOut},
    summary="Igreja atualiza um membro",
    description=(
        "Apenas a Igreja autenticada pode atualizar membros. "
        "O membro recebe um e-mail com senha temporária e link de verificação."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def update_membership_router(
    request,
    membership_id: uuid.UUID,
    payload: MemberChurchUpdateIn
):
    church = request.auth.church
    
    try:
        update_data = payload.dict(exclude_unset=True)
        
        
        updated_membership = update_member_church_service(
            member_church_id=membership_id,
            church_id=church.id,
            **update_data
        )
        
        # 3. Retornar resposta
        return 201, MemberChurchOut.from_orm(updated_membership)
        
    except MemberChurch.DoesNotExist as e:
        return 404, {"detail": str(e)}
        
    except ValueError as e:
        return 400, {"detail": str(e)}
        
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}
        
    except Exception as e:
        # Log do erro aqui
        return 400, {"detail": f"Erro ao atualizar membro: {str(e)}"}
#________________________________________________________________________


@router.patch(
    "/members/{membership_id}/profile",
    auth=ChurchOnlyAuth(),
    response={201: MemberOut, 404: MessageOut, 409: MessageOut},
    summary="Igreja atualiza perfil de um membro",
    description=(
        "Apenas a Igreja autenticada pode atualizar o perfil de um membro."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def update_member_church_profile_router(
    request,
    membership_id: uuid.UUID,
    payload: MemberUpdateIn
):
    church = request.auth.church
    
    try:
        # 1. Buscar o vínculo pelo ID
        membership = get_member_church_by_id(membership_id)
        if not membership:
            return 404, {"detail": "Vínculo não encontrado"}
        
        # 2. Verificar se o vínculo pertence à igreja autenticada
        if membership.church.id != church.id:
            return 404, {"detail": "Membro não encontrado nesta igreja"}
        
        # 3. Pegar o User associado ao membro
        user = membership.member.user
        
        # 4. Atualizar o perfil
        updated_member = update_member_profile(user, payload)
        
        # 5. Retornar o membro atualizado
        return 201, MemberOut.from_orm(updated_member)
        
    except MemberChurch.DoesNotExist as e:
        return 404, {"detail": str(e)}
        
    except ValueError as e:
        return 400, {"detail": str(e)}
        
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}
        
    except Exception as e:
        # Log do erro aqui
        return 400, {"detail": f"Erro ao atualizar perfil: {str(e)}"}
    

#______________________________________________________
@router.delete(
    "/members/{membership_id}",
    auth=ChurchOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Igreja remove o vínculo com um membro",
    description=(
        "Remove o vínculo (MemberChurch) entre a Igreja autenticada e o membro informado. "
        "O cadastro do membro (User/Member) não é excluído, apenas o vínculo com esta igreja."
    ),
)
@ratelimit(key="user", rate="30/m", block=True)
def church_delete_member(request, membership_id: uuid.UUID):
    church = request.auth.church
    try:
        delete_member_church_service(membership_id, church.id)
    except MemberChurch.DoesNotExist as e:
        return 404, {"detail": str(e)}
    return 200, {"detail": "Vínculo removido com sucesso."}

#_______________________________________________________________

@router.get(
    "/members/{membership_id}",
    auth=ChurchOnlyAuth(),
    response={
        200: MemberChurchOut,
        404: MessageOut,
        401: MessageOut,
    },
)
@ratelimit(key="user", rate="30/m", block=True)
def get_church_membership_router(
    request,
    membership_id: uuid.UUID,
):
    church = request.auth.church

    try:
        membership, _ = (
            get_church_membership_service(
                membership_id,
                church.id,
            )
        )

    except MemberChurch.DoesNotExist as e:
        return 404, {
            "detail": str(e)
        }

    return 200, MemberChurchOut.from_orm(
        membership
    )