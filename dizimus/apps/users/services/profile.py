"""
Profile Services — atualização de perfis específicos (Church/Member).
"""
from dizimus.apps.users.models import User, Church, Member
from dizimus.apps.users import repositories
from dizimus.apps.users.exceptions import UserAlreadyExists
from dizimus.apps.users.schemas.profile_schemas import ChurchUpdateIn, MemberUpdateIn


def _get_church(user: User) -> Church:
    church, _ = Church.objects.get_or_create(user=user)
    return church


def _get_member(user: User) -> Member:
    member, _ = Member.objects.get_or_create(user=user)
    return member


def update_church_profile(user: User, data: ChurchUpdateIn) -> Church:
    """
    Atualiza o perfil da Igreja.
    Valida unicidade de CNPJ antes de persistir.
    """
    payload = data.model_dump(exclude_none=True)

    if "cnpj" in payload:
        if Church.objects.filter(cnpj=payload["cnpj"]).exclude(user=user).exists():
            raise UserAlreadyExists("CNPJ")
    return repositories.update_church_profile(_get_church(user), **payload)


def update_member_profile(user: User, data: MemberUpdateIn) -> Member:
    """
    Atualiza o perfil do Membro.
    Valida unicidade de CPF antes de persistir.
    """
    payload = data.model_dump(exclude_none=True)

    if "cpf" in payload:
        if Member.objects.filter(cpf=payload["cpf"]).exclude(user=user).exists():
            raise UserAlreadyExists("CPF")
    return repositories.update_member_profile(_get_member(user), **payload)