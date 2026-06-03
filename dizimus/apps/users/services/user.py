"""
User Services — criação e atualização de usuário base.
"""
from dizimus.apps.users.models import User
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.selectors import email_exists, username_exists
from dizimus.apps.users.schemas import RegisterIn, UserUpdateIn


def register_user(data: RegisterIn) -> dict:
    """
    Cria o User + perfil (Church ou Member) e dispara e-mail de verificação.
    Retorna os tokens JWT diretamente para o cliente já poder operar.
    """
    if email_exists(data.email):
        raise UserAlreadyExists("e-mail")
    user = repositories.create_user(
        email=data.email,
        password=data.password,
        role=data.user_label,
        phone=data.phone,
    )

    if user.role == User.UserRole.CHURCH:
        repositories.create_church_profile(user)
    else:
        repositories.create_member_profile(user)

    from dizimus.apps.users.tasks.verification import send_verification_email
    send_verification_email.delay(user.pk)

    from .auth import _make_tokens
    return _make_tokens(user)


def update_user_profile(user: User, data: UserUpdateIn) -> User:
    payload = data.model_dump(exclude_none=True)

    if "username" in payload and username_exists(payload["username"], exclude_id=user.pk):
        raise UserAlreadyExists("username")

    return repositories.update_user(user, **payload)