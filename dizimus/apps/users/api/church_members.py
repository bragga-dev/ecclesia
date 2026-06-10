"""
Church Members router — Igreja cadastra seus membros.
"""
from typing import List
from ninja import Router
from dizimus.apps.users.permissions import ChurchOnlyAuth
from dizimus.apps.users.models import User
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.schemas.member_schemas import ChurchRegisterMemberIn, MemberInviteOut, ChurchMemberListOut
from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.users.services.church_member import register_member_by_church
from django_ratelimit.decorators import ratelimit

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



@router.get("/members", auth=ChurchOnlyAuth(), response={200: List[ChurchMemberListOut]},
    summary="Igreja lista seus membros",
    description="Retorna todos os membros vinculados à igreja autenticada.",
)
@ratelimit(key="user", rate="30/m", block=True,)
def church_list_members(request):
    user: User = request.auth
    church = user.church

    from dizimus.apps.community.models.member_church_model import MemberChurch
    memberships = (
        MemberChurch.objects
        .filter(church=church)
        .select_related("member__user")
        .order_by("-joined_at")
    )

    return 200, [ChurchMemberListOut.from_membership(m) for m in memberships]