"""
Sistema de permissões baseado em MemberChurch.
Verifica se um membro tem permissões específicas em uma igreja.
"""
from typing import Union, List
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils import timezone

from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.member_church_permission import MemberChurchPermission
from ecclesia.apps.users.permissions.request_helpers import get_church_id_from_request


def _get_effective_permission_codes(member_church: MemberChurch):
    """Retorna os códigos de permissão efetivos de um MemberChurch."""
    return MemberChurchPermission.objects.filter(
        member_church=member_church,
        is_active=True,
        permission__is_active=True,
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
    ).values_list("permission__code", flat=True)


def _get_member_church(request, church_id):
    """
    Busca o MemberChurch ativo do usuário na igreja.
    Levanta PermissionDenied se não encontrado.
    """
    try:
        return MemberChurch.objects.select_related(
            "member", "church"
        ).get(
            member__user=request.user,
            church_id=church_id,
            status=MemberChurch.Status.ACTIVE,
        )
    except MemberChurch.DoesNotExist:
        raise PermissionDenied("Usuário não é membro ativo desta igreja.")


def _base_check(request, church_id_param: str = "church_id"):
    """
    Validações comuns a todos os checkers:
    autenticação, superuser bypass e extração do church_id.
    Retorna (user, church_id) ou levanta PermissionDenied.
    """
    if not request.user or isinstance(request.user, AnonymousUser):
        raise PermissionDenied("Usuário não autenticado.")

    if request.user.is_superuser:
        return request.user, None  # superuser — sem necessidade de church_id

    church_id = get_church_id_from_request(request, church_id_param)
    if not church_id:
        raise PermissionDenied("ID da igreja não fornecido.")

    return request.user, church_id


class MemberChurchPermissionChecker:
    """
    Verifica se o MemberChurch tem QUALQUER UMA das permissões listadas.
    """

    def __init__(
        self,
        permission_codes: Union[str, List[str]],
        church_id_param: str = "church_id",
    ):
        self.permission_codes = (
            [permission_codes]
            if isinstance(permission_codes, str)
            else permission_codes
        )
        self.church_id_param = church_id_param

    def check(self, request) -> bool:
        user, church_id = _base_check(request, self.church_id_param)

        if user.is_superuser:
            return True

        member_church = _get_member_church(request, church_id)
        effective = set(_get_effective_permission_codes(member_church))

        if any(code in effective for code in self.permission_codes):
            return True

        raise PermissionDenied(
            f"Permissão negada. Necessário: {', '.join(self.permission_codes)}"
        )


class MemberChurchAllPermissionsChecker:
    """
    Verifica se o MemberChurch tem TODAS as permissões listadas.
    """

    def __init__(
        self,
        permission_codes: List[str],
        church_id_param: str = "church_id",
    ):
        self.permission_codes = permission_codes
        self.church_id_param = church_id_param

    def check(self, request) -> bool:
        user, church_id = _base_check(request, self.church_id_param)

        if user.is_superuser:
            return True

        member_church = _get_member_church(request, church_id)
        effective = set(_get_effective_permission_codes(member_church))
        requested = set(self.permission_codes)

        if requested.issubset(effective):
            return True

        missing = requested - effective
        raise PermissionDenied(f"Permissões faltando: {', '.join(missing)}")