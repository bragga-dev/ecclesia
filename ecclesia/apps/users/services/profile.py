"""
Profile Services — atualização de perfis específicos (Church/Member).
"""
from ecclesia.apps.users.models import User, Church, Member
from ecclesia.apps.users import repositories
from ecclesia.apps.users.exceptions import UserAlreadyExists
from ecclesia.apps.users.schemas.church_schemas import ChurchUpdateIn
from ecclesia.apps.users.schemas.member_schemas import MemberUpdateIn
from ecclesia.apps.users.selectors.church_selector import get_church_by_cnpj
from ecclesia.apps.users.selectors.member_selector import  get_member_by_cpf


def _get_church(user: User) -> Church:
    church, _ = Church.objects.get_or_create(user=user)
    return church


def _get_member(user: User) -> Member:
    member, _ = Member.objects.get_or_create(user=user)
    return member


def update_church_profile(user: User, data: ChurchUpdateIn) -> Church:
    payload = data.model_dump(exclude_none=True)

    if "church_label" in payload:
        payload["church_type"] = payload.pop("church_label")

    if "cnpj" in payload:
        existing_church = get_church_by_cnpj(payload["cnpj"])
        if existing_church and existing_church.user != user:
            raise UserAlreadyExists("CNPJ já cadastrado para outra igreja")

    return repositories.update_church_profile(_get_church(user), **payload)


def update_member_profile(user: User, data: MemberUpdateIn) -> Member:
    payload = data.model_dump(exclude_none=True)

    # contribution_label já foi convertido para o valor interno pelo field_validator
    # mas o model usa contribution_type — renomeia antes de salvar
    if "contribution_label" in payload:
        payload["contribution_type"] = payload.pop("contribution_label")

    if "cpf" in payload:
        existing_member = get_member_by_cpf(payload["cpf"])
        if existing_member and existing_member.user != user:
            raise UserAlreadyExists("CPF já cadastrado para outro membro")

    return repositories.update_member_profile(_get_member(user), **payload)