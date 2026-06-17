"""
MemberChurch Services — Igreja cadastra e lista membros.
Pertence ao app community.
"""
import secrets
import string
import uuid

from django.db.models import QuerySet
from dizimus.apps.community.selectors.member_church_selector import get_member_church
from dizimus.apps.community.repositories.member_church_repository import update_member_church
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.member import Member
from dizimus.apps.users.models.church import Church
from dizimus.apps.community.models.member_church_model import MemberChurch
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.selectors import email_exists
from dizimus.apps.community.repositories.member_church_repository import create_member_church   
from dizimus.apps.users.selectors.church_selector import get_church_by_id
from dizimus.apps.community.selectors.member_church_selector import (
    get_all_members_by_church_id,
    filter_members_by_status,
    filter_members_by_roles,
    filter_members_by_contribution,
)
from dizimus.apps.community.selectors.member_church_selector import get_member_church_by_id
from dizimus.apps.community.repositories.member_church_repository import update_member_church, delete_member_church_repository
   

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
    role: str = MemberChurch.Role.MEMBER,
    status: str = MemberChurch.Status.ACTIVE,
    contribution_type: str = MemberChurch.ContributionType.NONE,
) -> Member:
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

    create_member_church(
        member=user.member,
        church=church,
        role=role,
        status=status,
        contribution_type=contribution_type,
    )

    from dizimus.apps.users.tasks.member_invite import send_member_invite_email
    send_member_invite_email.delay(str(user.pk), temp_password)

    return user.member


def list_member_church_service(church_id: uuid.UUID,  *,  status: str | None = MemberChurch.Status.ACTIVE,
    roles: list[str] | None = None,  contribution_types: list[str] | None = None,) -> QuerySet[MemberChurch]:
    if not get_church_by_id(church_id):
        return MemberChurch.objects.none()

    queryset = get_all_members_by_church_id(church_id)

    if status:
        queryset = filter_members_by_status(queryset, status)

    if roles:
        queryset = filter_members_by_roles(queryset, roles)

    if contribution_types:
        queryset = filter_members_by_contribution(queryset, contribution_types)

    return queryset




def update_member_church_service(
    member_church_id: uuid.UUID, 
    church_id: uuid.UUID,
    **fields
) -> MemberChurch:
    if not fields:
        raise ValueError("Nenhum campo fornecido para atualização")
    member_church = get_member_church(member_church_id, church_id)
    if not member_church:
        raise MemberChurch.DoesNotExist(
            f"MemberChurch com id {member_church_id} não encontrado para esta igreja"
        )
    try:
        return update_member_church(member_church, **fields)
    except Exception as e:
        raise


def delete_member_church_service(membership_id: uuid.UUID,  church_id: uuid.UUID,) -> None:
    membership = get_member_church_by_id(membership_id)
    if not membership or membership.church_id != church_id:
        raise MemberChurch.DoesNotExist(f"MemberChurch com id {membership} não encontrado para esta igreja")
    delete_member_church_repository(membership)