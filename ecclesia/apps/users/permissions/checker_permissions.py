"""
Sistema de permissões baseado em MemberChurch.
Verifica se um membro tem permissões específicas em uma igreja.
"""
from typing import Union, List, Optional
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils import timezone

from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.member_church_permission import MemberChurchPermission
from ecclesia.apps.users.models.system_permission import SystemPermission


class MemberChurchPermissionChecker:
    """
    Classe para verificar permissões de um MemberChurch.
    
    Fluxo:
    1. Obtém o MemberChurch (vínculo ativo) do usuário na igreja atual
    2. Verifica se o MemberChurch tem a permissão solicitada via MemberChurchPermission
    """
    
    def __init__(self, permission_codes: Union[str, List[str]], church_id_param: str = "church_id"):
        """
        Args:
            permission_codes: Código da permissão ou lista de códigos (qualquer um basta)
            church_id_param: Nome do parâmetro na requisição que contém o ID da igreja
        """
        self.permission_codes = [permission_codes] if isinstance(permission_codes, str) else permission_codes
        self.church_id_param = church_id_param
    
    def check(self, request) -> bool:
        """
        Verifica se o usuário tem permissão.
        Retorna True ou lança PermissionDenied.
        """
        # 1. Usuário não autenticado
        if not request.user or isinstance(request.user, AnonymousUser):
            raise PermissionDenied("Usuário não autenticado.")
        
        # 2. Superusuário tem acesso total
        if request.user.is_superuser:
            return True
        
        # 3. Obtém o ID da igreja do contexto
        church_id = self._get_church_id(request)
        if not church_id:
            raise PermissionDenied("ID da igreja não fornecido.")
        
        # 4. Busca o MemberChurch (vínculo) do usuário nesta igreja
        try:
            member_church = MemberChurch.objects.select_related(
                'member', 'church'
            ).get(
                member__user=request.user,
                church_id=church_id,
                status=MemberChurch.Status.ACTIVE
            )
        except MemberChurch.DoesNotExist:
            raise PermissionDenied("Usuário não é membro ativo desta igreja.")
        
        # 5. Verifica se o MemberChurch tem alguma das permissões solicitadas
        if self._has_permission(member_church):
            return True
        
        raise PermissionDenied(
            f"Permissão negada. Você precisa de uma das permissões: {', '.join(self.permission_codes)}"
        )
    
    def _get_church_id(self, request):
        """Extrai o ID da igreja da requisição."""
        # Tentar path params (FastAPI/DRF)
        if hasattr(request, 'path_params'):
            church_id = request.path_params.get(self.church_id_param)
            if church_id:
                return church_id
        
        # Tentar query params
        if hasattr(request, 'query_params'):
            church_id = request.query_params.get(self.church_id_param)
            if church_id:
                return church_id
        
        # Tentar request body (JSON)
        if hasattr(request, 'data'):
            church_id = request.data.get(self.church_id_param)
            if church_id:
                return church_id
        
        # Tentar atributo do request (DRF)
        if hasattr(request, 'parser_context'):
            kwargs = request.parser_context.get('kwargs', {})
            church_id = kwargs.get(self.church_id_param)
            if church_id:
                return church_id
        
        # Último recurso: tentar pegar do atributo church_id do request
        if hasattr(request, 'church_id'):
            return request.church_id
        
        return None
    
    def _has_permission(self, member_church: MemberChurch) -> bool:
        """Verifica se o MemberChurch tem pelo menos uma das permissões solicitadas."""
        # Busca as permissões efetivas do MemberChurch
        effective_permissions = MemberChurchPermission.objects.filter(
            member_church=member_church,
            is_active=True,
            permission__is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).values_list('permission__code', flat=True)
        
        # Verifica se alguma das permissões solicitadas está presente
        for code in self.permission_codes:
            if code in effective_permissions:
                return True
        
        return False


class MemberChurchAllPermissionsChecker:
    """
    Verifica se o MemberChurch tem TODAS as permissões listadas.
    """
    
    def __init__(self, permission_codes: List[str], church_id_param: str = "church_id"):
        self.permission_codes = permission_codes
        self.church_id_param = church_id_param
    
    def check(self, request) -> bool:
        if not request.user or isinstance(request.user, AnonymousUser):
            raise PermissionDenied("Usuário não autenticado.")
        
        if request.user.is_superuser:
            return True
        
        church_id = self._get_church_id(request)
        if not church_id:
            raise PermissionDenied("ID da igreja não fornecido.")
        
        try:
            member_church = MemberChurch.objects.select_related(
                'member', 'church'
            ).get(
                member__user=request.user,
                church_id=church_id,
                status=MemberChurch.Status.ACTIVE
            )
        except MemberChurch.DoesNotExist:
            raise PermissionDenied("Usuário não é membro ativo desta igreja.")
        
        # Obtém todas as permissões efetivas do MemberChurch
        user_permissions = set(
            MemberChurchPermission.objects.filter(
                member_church=member_church,
                is_active=True,
                permission__is_active=True
            ).filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
            ).values_list('permission__code', flat=True)
        )
        
        # Verifica se TODAS as permissões solicitadas estão presentes
        requested = set(self.permission_codes)
        if requested.issubset(user_permissions):
            return True
        
        missing = requested - user_permissions
        raise PermissionDenied(
            f"Permissões faltando: {', '.join(missing)}"
        )
    
    def _get_church_id(self, request):
        # Mesma lógica do MemberChurchPermissionChecker._get_church_id
        if hasattr(request, 'path_params'):
            church_id = request.path_params.get(self.church_id_param)
            if church_id:
                return church_id
        
        if hasattr(request, 'query_params'):
            church_id = request.query_params.get(self.church_id_param)
            if church_id:
                return church_id
        
        if hasattr(request, 'data'):
            church_id = request.data.get(self.church_id_param)
            if church_id:
                return church_id
        
        if hasattr(request, 'parser_context'):
            kwargs = request.parser_context.get('kwargs', {})
            church_id = kwargs.get(self.church_id_param)
            if church_id:
                return church_id
        
        if hasattr(request, 'church_id'):
            return request.church_id
        
        return None