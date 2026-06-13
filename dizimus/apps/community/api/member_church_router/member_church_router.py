"""
Church Members router — Igreja cadastra e lista seus membros.
"""
from ninja import Router, Query
from dizimus.apps.users.permissions import ChurchOnlyAuth
from dizimus.apps.users.models import User
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.community.schemas.member_church_schema import (   
    ChurchRegisterMemberIn,
    MemberInviteOut,
    ChurchMemberListOut,
)
from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.community.services.member_church_service import (
    register_member_by_church,
    list_member_church_service,
)
from dizimus.apps.community.models.member_church_model import MemberChurch
from django_ratelimit.decorators import ratelimit
from dizimus.apps.users.utils.pagination import paginate_queryset, PageOut

router = Router(tags=["Churches"])


@router.post("/members", auth=ChurchOnlyAuth(), response={201: MemberInviteOut, 409: MessageOut},
    summary="Igreja cadastra um membro",
    description=(
        "Apenas a Igreja autenticada pode cadastrar membros. "
        "O membro recebe um e-mail com senha temporária e link de verificação."
    ),
)
@ratelimit(key="user", rate="30/m", block=True,)
def church_register_member(request, payload: ChurchRegisterMemberIn):
    user: User = request.auth
    church = user.church

    try:
        member = register_member_by_church(
            church=church,
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}

    return 201, MemberInviteOut(
        id=member.user.id,
        email=member.user.email,
        first_name=member.first_name,
        last_name=member.last_name,
    )


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