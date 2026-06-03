"""
Profile Services — atualização de perfis específicos (Church/Member).
"""
from dizimus.apps.users.models import User, Church, Member
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.schemas.church_schemas import ChurchUpdateIn
from dizimus.apps.users.schemas.member_schemas import MemberUpdateIn
from dizimus.apps.users.selectors.church_selector import get_church_by_cnpj
from dizimus.apps.users.selectors.member_selector import  get_member_by_cpf


def _get_church(user: User) -> Church:
    church, _ = Church.objects.get_or_create(user=user)
    return church


def _get_member(user: User) -> Member:
    member, _ = Member.objects.get_or_create(user=user)
    return member


def update_church_profile(user: User, data: ChurchUpdateIn) -> Church:
    payload = data.model_dump(exclude_none=True)
    if "cnpj" in payload:
        existing_church = get_church_by_cnpj(payload["cnpj"])
        if existing_church and existing_church.user != user:
            raise UserAlreadyExists("CNPJ já cadastrado para outra igreja")
    return repositories.update_church_profile(_get_church(user), **payload)



def update_member_profile(user: User, data: MemberUpdateIn) -> Member:
    payload = data.model_dump(exclude_none=True)
    if "cpf" in payload:
        existing_member = get_member_by_cpf(payload["cpf"])
        if existing_member and existing_member.user != user:
            raise UserAlreadyExists("CPF já cadastrado para outro membro")
    return repositories.update_member_profile(_get_member(user), **payload)