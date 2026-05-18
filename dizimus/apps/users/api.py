"""
Users router — endpoints autenticados de perfil.
Registrado em config/api.py como: api.add_router("/users/", ...)
"""
import uuid
from typing import List

from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import File, Router, UploadedFile
from ninja_jwt.authentication import JWTAuth

from dizimus.apps.users import repositories, services
from dizimus.apps.users.exceptions import PermissionDenied, UserAlreadyExists
from dizimus.apps.users.models import User
from dizimus.apps.users.schemas.profile_schemas import (
    AddressIn,
    AddressOut,
    AddressUpdateIn,
    ChurchProfileOut,
    ChurchUpdateIn,
    MemberProfileOut,
    MemberUpdateIn,
)
from dizimus.apps.users.schemas.users_schemas import MessageOut, UserOut, UserUpdateIn
from dizimus.apps.users.validators import validate_image_file

router = Router(auth=JWTAuth())


# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL BASE (User)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/me",
    response=UserOut,
    summary="Meu perfil",
)
def get_me(request):
    """Retorna os dados do usuário autenticado."""
    return request.auth


@router.patch(
    "/me",
    response={200: UserOut, 409: MessageOut},
    summary="Atualizar dados base",
    description=(
        "Atualiza campos do usuário base: `username`, `first_name`, `last_name`, `phone`. "
        "Para campos específicos do perfil (CNPJ, CPF, etc.) use `PATCH /me/profile`."
    ),
)
def update_me(request, payload: UserUpdateIn):
    try:
        user = services.update_user_profile(request.auth, payload)
        return 200, user
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}


# ── Foto ──────────────────────────────────────────────────────────────────────

@router.post(
    "/me/photo",
    response={200: UserOut, 400: MessageOut},
    summary="Upload de foto de perfil",
)
def upload_photo(request, photo: UploadedFile = File(...)):
    """Formatos aceitos: jpg, jpeg, png, webp. Máx: 5 MB."""
    try:
        validate_image_file(photo)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}

    user = repositories.set_user_photo(request.auth, photo)
    return 200, user


@router.delete(
    "/me/photo",
    response={200: MessageOut},
    summary="Remover foto de perfil",
)
def remove_photo(request):
    """Restaura a imagem padrão."""
    repositories.remove_user_photo(request.auth)
    return 200, {"detail": "Foto removida com sucesso."}


# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL ESPECÍFICO (Church | Member)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/me/profile",
    response={200: ChurchProfileOut | MemberProfileOut},
    summary="Dados do perfil específico",
    description="Retorna `ChurchProfileOut` para Igrejas ou `MemberProfileOut` para Membros.",
)
def get_my_profile(request):
    user: User = request.auth
    if user.role == User.UserRole.CHURCH:
        return 200, user.church
    return 200, user.member


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


# ═══════════════════════════════════════════════════════════════════════════════
# ENDEREÇOS
# Funciona para Church e Member — o service detecta o role automaticamente.
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/me/addresses",
    response=List[AddressOut],
    summary="Listar endereços",
)
def list_addresses(request):
    """Retorna todos os endereços do usuário. O endereço principal aparece primeiro."""
    return services.list_my_addresses(request.auth)


@router.post(
    "/me/addresses",
    response={201: AddressOut, 422: MessageOut},
    summary="Adicionar endereço",
    description=(
        "Cria um novo endereço para o usuário. "
        "Se `principal=true`, os demais endereços são automaticamente desmarcados como principal."
    ),
)
def create_address(request, payload: AddressIn):
    try:
        address = services.create_my_address(request.auth, payload)
        return 201, address
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.patch(
    "/me/addresses/{address_id}",
    response={200: AddressOut, 404: MessageOut, 422: MessageOut},
    summary="Atualizar endereço",
)
def update_address(request, address_id: uuid.UUID, payload: AddressUpdateIn):
    try:
        address = services.update_my_address(request.auth, address_id, payload)
        if not address:
            return 404, {"detail": "Endereço não encontrado."}
        return 200, address
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.delete(
    "/me/addresses/{address_id}",
    response={200: MessageOut, 404: MessageOut},
    summary="Remover endereço",
)
def delete_address(request, address_id: uuid.UUID):
    deleted = services.delete_my_address(request.auth, address_id)
    if not deleted:
        return 404, {"detail": "Endereço não encontrado."}
    return 200, {"detail": "Endereço removido com sucesso."}