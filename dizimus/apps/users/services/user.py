"""
User Services — criação e atualização de usuário base.
"""
from dizimus.apps.users.models import User
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.selectors import email_exists
from dizimus.apps.users.schemas import RegisterIn
from django.db import transaction
from ninja_jwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.db import transaction
from django.utils import timezone
from dizimus.apps.users.models.audit_user_model import AuditLog 


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
        role=data.role,
    )

    if user.role == User.UserRole.CHURCH:
        repositories.create_church_profile(user)
    else:
        repositories.create_member_profile(user)

    from dizimus.apps.users.tasks.verification import send_verification_email
    send_verification_email.delay(user.pk)

    from .auth import _make_tokens
    return _make_tokens(user)


@transaction.atomic
def deactivate_account(user, performed_by=None, reason="Desativação de conta"):
    """ Desativa usuário, revoga todos os tokens ativos e cria logger de auditória"""
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)
    user.is_active = False
    user.save(update_fields=["is_active"])
    AuditLog.objects.create(
        action="DEACTIVATE_ACCOUNT",
        user=user,
        performed_by=performed_by,  
        reason=reason,
        timestamp=timezone.now(),
        details={
            "tokens_revoked": True,
            "user_id": str(user.id),
            "email": user.email,
        }
    )
