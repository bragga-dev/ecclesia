"""
Users router — endpoints de perfil base e foto.
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import File, Router, UploadedFile
from dizimus.apps.users.permissions.auth_classes import VerifiedUserAuth
from dizimus.apps.users import repositories, services
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.schemas.users_schemas import MessageOut, UserOut
from dizimus.apps.users.validators.validate_image_file import validate_image_file
from django_ratelimit.decorators import ratelimit

router = Router(auth=VerifiedUserAuth())

# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL BASE (User)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/me", response=UserOut, summary="Meu perfil",)
def get_me(request):
    """Retorna os dados do usuário autenticado."""
    return request.auth


# ── Foto ──────────────────────────────────────────────────────────────────────

@router.get("/me/photo", response={200: UserOut}, summary="Ver foto de perfil",)
def get_photo(request):
    """Retorna o usuário com a URL da foto atual."""
    return 200, request.auth


@router.post("/me/photo", response={200: UserOut, 400: MessageOut}, summary="Upload de foto de perfil",)
@ratelimit(key="user", rate="20/h", block=True,)
def upload_photo(request, photo: UploadedFile = File(...)):
    """Adiciona ou substitui a foto. Formatos: jpg, jpeg, png, webp. Máx: 5 MB."""
    try:
        validate_image_file(photo)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}
    user = repositories.set_user_photo(request.auth, photo)
    return 200, user


@router.patch("/me/photo", response={200: UserOut, 400: MessageOut}, summary="Atualizar foto de perfil",)
@ratelimit(key="user", rate="30/h", block=True,)
def update_photo(request, photo: UploadedFile = File(...)):
    """Substitui a foto existente. Formatos: jpg, jpeg, png, webp. Máx: 5 MB."""
    try:
        validate_image_file(photo)
    except DjangoValidationError as e:
        return 400, {"detail": str(e.message)}
    user = repositories.set_user_photo(request.auth, photo)
    return 200, user


@router.delete("/me/photo",  response={200: MessageOut}, summary="Remover foto de perfil",)
@ratelimit(key="user", rate="20/h", block=True,)
def remove_photo(request):
    """Restaura a imagem padrão."""
    repositories.remove_user_photo(request.auth)
    return 200, {"detail": "Foto removida com sucesso."}