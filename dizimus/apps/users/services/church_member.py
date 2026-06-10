"""
Church Member Services — Igreja cadastra membros.
"""
import secrets
import string

from dizimus.apps.users.models import User, Church, Member
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.selectors import email_exists


def _generate_temp_password(length: int = 12) -> str:
    """Gera senha temporária segura: letras + dígitos + símbolos."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    pwd = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%"),
    ]
    pwd += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def register_member_by_church(
    church: Church,
    email: str,
    first_name: str,
    last_name: str,
) -> Member:
    """
    Igreja cadastra um membro:
    1. Cria User com role=member e senha temporária
    2. Cria Member com first_name e last_name
    3. Cria MemberChurch vinculando membro à igreja (status=PENDING)
    4. Dispara e-mail com senha temporária e link de verificação
    """
    if email_exists(email):
        raise UserAlreadyExists("e-mail")

    temp_password = _generate_temp_password()

    user = repositories.create_user(
        email=email,
        password=temp_password,
        role=User.UserRole.MEMBER,
    )

    repositories.create_member_profile(
        user,
        first_name=first_name,
        last_name=last_name,
    )

    # Cria o vínculo com a igreja que está cadastrando
    from dizimus.apps.community.models.member_church_model import MemberChurch
    MemberChurch.objects.create(
        member=user.member,
        church=church,
        role=MemberChurch.Role.MEMBER,
        status=MemberChurch.Status.ACTIVE,
    )

    from dizimus.apps.users.tasks.member_invite import send_member_invite_email
    send_member_invite_email.delay(str(user.pk), temp_password)

    return user.member