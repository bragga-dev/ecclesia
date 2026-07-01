"""
Decoradores e classes de permissão para Django Ninja.
"""
from functools import wraps
from typing import Union, List, Optional
from ninja.security import HttpBearer

from .system_permissions import (
    MemberChurchPermissionChecker,
    MemberChurchAllPermissionsChecker
)
from ecclesia.apps.users.exceptions.permissions import PermissionDenied


class ChurchPermission(HttpBearer):
    """
    Classe de autenticação/autorização para Django Ninja.
    Combina autenticação JWT + verificação de permissão.
    
    Uso no Django Ninja:
        @router.post("/members", auth=ChurchPermission("members.create"))
        def create_member(request):
            ...
    """
    
    def __init__(self, permission_code: Union[str, List[str]]):
        super().__init__()
        self.permission_codes = [permission_code] if isinstance(permission_code, str) else permission_code
        self.checker = MemberChurchPermissionChecker(permission_code)
    
    def authenticate(self, request, token: str):
        """
        Método do Django Ninja para autenticação.
        """
        # 1. Valida o token JWT (usando sua auth existente)
        # Aqui você deve usar seu sistema de autenticação atual
        user = self._validate_token(token)
        if not user:
            return None
        
        request.user = user
        
        # 2. Pega o church_id da URL ou body
        church_id = self._get_church_id(request)
        if not church_id:
            # Se não encontrar church_id, não pode autenticar
            return None
        
        # 3. Verifica permissão
        try:
            self.checker.check(request, church_id)
            return user
        except PermissionDenied:
            return None
    
    def _validate_token(self, token: str):
        """
        Valida o token JWT usando seu sistema existente.
        """
        from ecclesia.apps.users.services.auth import AuthService
        # Adapte para seu serviço de autenticação
        return AuthService.validate_token(token)
    
    def _get_church_id(self, request):
        """
        Extrai o ID da igreja da requisição.
        """
        # Tenta pegar da URL (path params)
        if hasattr(request, 'path_params'):
            church_id = request.path_params.get('church_id')
            if church_id:
                return church_id
        
        # Tenta pegar do body (JSON)
        if hasattr(request, 'body'):
            import json
            try:
                data = json.loads(request.body)
                church_id = data.get('church_id')
                if church_id:
                    return church_id
            except:
                pass
        
        # Tenta pegar do query params
        if hasattr(request, 'GET'):
            church_id = request.GET.get('church_id')
            if church_id:
                return church_id
        
        return None


class HasPermission:
    """
    Classe para verificação de permissão em rotas do Django Ninja.
    Usa o sistema de autenticação existente + verificação de permissão.
    
    Uso:
        @router.post("/members", auth=HasPermission("members.create"))
        def create_member(request):
            ...
    """
    
    def __init__(self, permission_code: Union[str, List[str]]):
        self.permission_codes = [permission_code] if isinstance(permission_code, str) else permission_code
        self.checker = MemberChurchPermissionChecker(permission_code)
    
    def __call__(self, request):
        """
        Método chamado pelo Django Ninja para autenticação.
        """
        # 1. Verifica se o usuário está autenticado (usando seu sistema)
        if not hasattr(request, 'user') or not request.user:
            return None
        
        # 2. Superusuário passa direto
        if request.user.is_superuser:
            return request.user
        
        # 3. Pega o church_id
        church_id = self._get_church_id(request)
        if not church_id:
            return None
        
        # 4. Verifica permissão
        try:
            self.checker.check(request, church_id)
            return request.user
        except PermissionDenied:
            return None
    
    def _get_church_id(self, request):
        """Extrai o ID da igreja da requisição."""
        # Tenta path params
        if hasattr(request, 'path_params'):
            church_id = request.path_params.get('church_id')
            if church_id:
                return church_id
        
        # Tenta body
        if hasattr(request, 'body'):
            import json
            try:
                data = json.loads(request.body)
                church_id = data.get('church_id')
                if church_id:
                    return church_id
            except:
                pass
        
        # Tenta query params
        if hasattr(request, 'GET'):
            church_id = request.GET.get('church_id')
            if church_id:
                return church_id
        
        return None


class HasAllPermissions:
    """
    Verifica se o usuário tem TODAS as permissões listadas.
    
    Uso:
        @router.delete("/members/{id}", auth=HasAllPermissions(["members.view", "members.delete"]))
        def delete_member(request):
            ...
    """
    
    def __init__(self, permission_codes: List[str]):
        self.permission_codes = permission_codes
        self.checker = MemberChurchAllPermissionsChecker(permission_codes)
    
    def __call__(self, request):
        if not hasattr(request, 'user') or not request.user:
            return None
        
        if request.user.is_superuser:
            return request.user
        
        church_id = self._get_church_id(request)
        if not church_id:
            return None
        
        try:
            self.checker.check(request, church_id)
            return request.user
        except PermissionDenied:
            return None
    
    def _get_church_id(self, request):
        """Extrai o ID da igreja da requisição."""
        if hasattr(request, 'path_params'):
            church_id = request.path_params.get('church_id')
            if church_id:
                return church_id
        
        if hasattr(request, 'body'):
            import json
            try:
                data = json.loads(request.body)
                church_id = data.get('church_id')
                if church_id:
                    return church_id
            except:
                pass
        
        if hasattr(request, 'GET'):
            church_id = request.GET.get('church_id')
            if church_id:
                return church_id
        
        return None


# ============================================================================
# Decorators Alternativos (se preferir usar decorators em vez de auth)
# ============================================================================

def require_permission(permission_code: Union[str, List[str]]):
    """
    Decorator para verificar permissão em funções Django Ninja.
    
    Uso:
        @router.post("/members")
        @require_permission("members.create")
        def create_member(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            checker = MemberChurchPermissionChecker(permission_code)
            
            # Pega o church_id dos kwargs (da URL)
            church_id = kwargs.get('church_id')
            if not church_id:
                church_id = request.path_params.get('church_id')
            
            if not church_id:
                raise PermissionDenied("ID da igreja não fornecido.")
            
            checker.check(request, church_id)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permission_codes: List[str]):
    """
    Decorator para verificar TODAS as permissões.
    
    Uso:
        @router.delete("/members/{id}")
        @require_all_permissions(["members.view", "members.delete"])
        def delete_member(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            checker = MemberChurchAllPermissionsChecker(permission_codes)
            
            church_id = kwargs.get('church_id')
            if not church_id:
                church_id = request.path_params.get('church_id')
            
            if not church_id:
                raise PermissionDenied("ID da igreja não fornecido.")
            
            checker.check(request, church_id)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator