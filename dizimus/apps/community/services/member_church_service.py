# services/church_member.py
"""
Church Member Services — Igreja cadastra e lista membros.
"""
import secrets
import string
import uuid

from django.db.models import QuerySet

from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.member import Member
from dizimus.apps.users.models.church import Church
from dizimus.apps.community.models.member_church_model import MemberChurch
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.selectors import email_exists
from dizimus.apps.community.selectors.member_church_selector import (
    get_all_churches_by_member_id,
    get_all_members_by_church_id, 
    filter_members_by_status,
    filter_members_by_roles,
    filter_members_by_contribution,
    filter_members_by_joined_after,
    search_members_in_church,
    get_member_church,
    get_member_church_by_id,

)


from dizimus.apps.users.selectors.church_selector import get_church_by_id


def _generate_temp_password(length: int = 12) -> str:
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
    1. Cria User com role=MEMBER e senha temporária
    2. Cria Member com first_name e last_name
    3. Cria MemberChurch vinculando membro à igreja (status=ACTIVE)
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

    MemberChurch.objects.create(
        member=user.member,
        church=church,
        role=MemberChurch.Role.MEMBER,
        status=MemberChurch.Status.ACTIVE,
    )

    from dizimus.apps.users.tasks.member_invite import send_member_invite_email
    send_member_invite_email.delay(str(user.pk), temp_password)

    return user.member


def list_member_church_service(church_id: uuid.UUID, *, status: str | None = MemberChurch.Status.ACTIVE,
    roles: list[str] | None = None, contribution_types: list[str]|None = None, ) -> QuerySet[MemberChurch]:
    """
    Lista membros da igreja aplicando filtros de negócio.

    Args:
        church_id: ID da igreja.
        status: Status do vínculo. None → retorna todos os status.
        roles: Lista de funções permitidas. None → retorna todos os roles.

    Returns:
        QuerySet[MemberChurch] vazio se a igreja não existir.
    """
    if not get_church_by_id(church_id):
        return MemberChurch.objects.none()

    queryset = get_all_members_by_church_id(church_id)

    if status is not None:
        queryset = filter_members_by_status(queryset, status)

    if roles:
        queryset = filter_members_by_roles(queryset, roles)

    if contribution_types:
        queryset = filter_members_by_contribution

    return queryset