"""
Users router — endpoints de perfil base e foto.
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import File, Router, UploadedFile
from ecclesia.apps.users.permissions.auth_classes import VerifiedUserAuth
from ecclesia.apps.users import repositories, services
from ecclesia.apps.users.exceptions import UserAlreadyExists
from ecclesia.apps.users.schemas.users_schemas import MessageOut, UserOut
from ecclesia.apps.users.validators.validate_image_file import validate_image_file
from django_ratelimit.decorators import ratelimit
from django.shortcuts import get_object_or_404
from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.community.schemas.member_church_schema import MemberChurchOut


router = Router(auth=VerifiedUserAuth())

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL BASE (User)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/me", response=UserOut, summary="Meu perfil",)
def get_me(request):
    """Retorna os dados do usuário autenticado."""
    return UserOut.from_orm(request.user)


# ── Foto ──────────────────────────────────────────────────────────────────────

@router.get("/me/photo", response={200: UserOut}, summary="Ver foto de perfil",)
def get_photo(request):
    """Retorna o usuário com a URL da foto atual."""
    return UserOut.from_orm(request.user)


@router.post("/me/photo", response={200: UserOut, 400: MessageOut}, summary="Upload de foto de perfil",)
@ratelimit(key="user", rate="20/h", block=True,)
def upload_photo(request, photo: UploadedFile = File(...)):
    """Adiciona ou substitui a foto. Formatos: jpg, jpeg, png, webp. Máx: 5 MB."""
    try:
        validate_image_file(photo)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}
    user = repositories.set_user_photo(request.auth, photo)
    return UserOut.from_orm(request.user)


@router.patch("/me/photo", response={200: UserOut, 400: MessageOut}, summary="Atualizar foto de perfil",)
@ratelimit(key="user", rate="30/h", block=True,)
def update_photo(request, photo: UploadedFile = File(...)):
    """Substitui a foto existente. Formatos: jpg, jpeg, png, webp. Máx: 5 MB."""
    try:
        validate_image_file(photo)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}
    user = repositories.set_user_photo(request.auth, photo)
    return UserOut.from_orm(request.user)


@router.delete("/me/photo",  response={200: MessageOut}, summary="Remover foto de perfil",)
@ratelimit(key="user", rate="20/h", block=True,)
def remove_photo(request):
    """Restaura a imagem padrão."""
    repositories.remove_user_photo(request.auth)
    return 200, {"detail": "Foto removida com sucesso."}


@router.delete("/me", response={204: None}, summary="Usuário deleta sua própria conta")
def delete_me(request):
    services.deactivate_account(request.auth)
    return 204, None

@router.get("/me/church", response=MemberChurchOut, summary="Retorna informações da igreja a qual o membro é vinculado")
@ratelimit(key="user", rate="100/h", block=True)
def get_my_church(request):
    membership = get_object_or_404(MemberChurch.objects.select_related("church__user"),
        member__user=request.auth,
        status=MemberChurch.Status.ACTIVE,
    )
    return MemberChurchOut.from_orm(membership.church)