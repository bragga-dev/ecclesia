"""
Users router — endpoints de perfis específicos (Church/Member) e banner.
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import File, Router, UploadedFile

from dizimus.apps.users import repositories, services
from dizimus.apps.users.exceptions import UserAlreadyExists, PermissionDenied
from dizimus.apps.users.models import User
from dizimus.apps.users.schemas.church_schemas import ChurchUpdateIn
from dizimus.apps.users.schemas.member_schemas import MemberUpdateIn
from dizimus.apps.users.schemas.profile_church_schema import ChurchProfileOut
from dizimus.apps.users.schemas.profile_member_schema import MemberProfileOut
from dizimus.apps.users.schemas.addresses_schemas import (
    AddressIn, AddressUpdateIn, AddressOut,
)

from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.users.validators.validate_image_file import validate_image_file

router = Router()

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL ESPECÍFICO (Church | Member)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/me/profile",
    response={200: ChurchProfileOut | MemberProfileOut, 403: MessageOut},
    summary="Obter meu perfil específico",
)
def get_my_profile(request):
    user: User = request.auth

    if user.role == User.UserRole.CHURCH:
        return 200, ChurchProfileOut.from_orm(user, user.church)

    if user.role == User.UserRole.MEMBER:
        return 200, MemberProfileOut.from_orm(user, user.member)

    return 403, {"detail": "Administradores não possuem perfil público."}


@router.patch(
    "/me/profile/church",
    response={200: ChurchProfileOut, 403: MessageOut, 409: MessageOut, 422: MessageOut},
    summary="Atualizar perfil Igreja",
)
def update_church_profile(request, payload: ChurchUpdateIn):
    user: User = request.auth
    if user.role != User.UserRole.CHURCH:
        return 403, {"detail": "Apenas Igrejas podem acessar este endpoint."}
    try:
        church = services.update_church_profile(user, payload)
        return 200, ChurchProfileOut.from_orm(user, church)
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.patch(
    "/me/profile/member",
    response={200: MemberProfileOut, 403: MessageOut, 409: MessageOut, 422: MessageOut},
    summary="Atualizar perfil Membro",
)
def update_member_profile(request, payload: MemberUpdateIn):
    user: User = request.auth
    if user.role != User.UserRole.MEMBER:
        return 403, {"detail": "Apenas Membros podem acessar este endpoint."}
    try:
        member = services.update_member_profile(user, payload)
        return 200, MemberProfileOut.from_orm(user, member)
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.post(
    "/me/banner",
    response={200: ChurchProfileOut, 400: MessageOut, 403: MessageOut},
    summary="Upload de banner (somente Igreja)",
)
def upload_banner(request, banner: UploadedFile = File(...)):
    user: User = request.auth
    if user.role != User.UserRole.CHURCH:
        return 403, {"detail": "Somente Igrejas podem ter banner."}
    try:
        validate_image_file(banner)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}
    church = repositories.set_church_banner(user.church, banner)
    return 200, ChurchProfileOut.from_orm(user, church)  # ← também precisava