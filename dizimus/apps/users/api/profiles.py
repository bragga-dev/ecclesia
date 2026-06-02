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

@router.get("/me/profile",  response={200: ChurchProfileOut | MemberProfileOut, 403: MessageOut, 404: MessageOut}, 
summary="Obter meu perfil específico", description="Retorna os dados do perfil de acordo com a role do usuário autenticado. Exclusivo para usuários com role `church` ou `member`.")

def get_my_profile(request):
    user: User = request.auth

    if user.role == User.UserRole.CHURCH:
        return 200, user.church

    if user.role == User.UserRole.MEMBER:
        return 200, user.member

    return 403, {
        "detail": "Administradores não possuem perfil público."
    }


@router.patch(
    "/me/profile/church",
    response={200: ChurchProfileOut, 403: MessageOut, 409: MessageOut, 422: MessageOut},
    summary="Atualizar perfil Igreja",
    description="Campos disponíveis: `cnpj`, `instagram`, `website`, `about`. Exclusivo para usuários com role `church`.",
)
def update_church_profile(request, payload: ChurchUpdateIn):
    user: User = request.auth
    if user.role != User.UserRole.CHURCH:
        return 403, {"detail": "Apenas Igrejas podem acessar este endpoint."}
    try:
        profile = services.update_church_profile(user, payload)
        return 200, profile
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.patch(
    "/me/profile/member",
    response={200: MemberProfileOut, 403: MessageOut, 409: MessageOut, 422: MessageOut},
    summary="Atualizar perfil Membro",
    description="Campos disponíveis: `cpf`, `date_of_birth`. Exclusivo para usuários com role `member`.",
)
def update_member_profile(request, payload: MemberUpdateIn):
    user: User = request.auth
    if user.role != User.UserRole.MEMBER:
        return 403, {"detail": "Apenas Membros podem acessar este endpoint."}
    try:
        profile = services.update_member_profile(user, payload)
        return 200, profile
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


# ── Banner (exclusivo de Igreja) ──────────────────────────────────────────────

@router.post(
    "/me/banner",
    response={200: ChurchProfileOut, 400: MessageOut, 403: MessageOut},
    summary="Upload de banner (somente Igreja)",
)
def upload_banner(request, banner: UploadedFile = File(...)):
    """Formatos aceitos: jpg, jpeg, png, webp. Máx: 5 MB."""
    user: User = request.auth
    if user.role != User.UserRole.CHURCH:
        return 403, {"detail": "Somente Igrejas podem ter banner."}

    try:
        validate_image_file(banner)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}

    church = repositories.set_church_banner(user.church, banner)
    return 200, church


@router.delete(
    "/me/banner",
    response={200: MessageOut, 403: MessageOut},
    summary="Remover banner (somente Igreja)",
)
def remove_banner(request):
    """Restaura o banner padrão."""
    user: User = request.auth
    if user.role != User.UserRole.CHURCH:
        return 403, {"detail": "Somente Igrejas podem ter banner."}

    repositories.remove_church_banner(user.church)
    return 200, {"detail": "Banner removido com sucesso."}