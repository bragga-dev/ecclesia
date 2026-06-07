"""
Auth Classes - Classes de autenticação com permissões embutidas.
"""
from ninja_jwt.authentication import JWTAuth
from dizimus.apps.users.exceptions import PermissionDenied
from .roles import is_church, is_member, is_admin, is_active, is_verified


# auth_classes.py
class ChurchOnlyAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and not is_admin(user) and not is_church(user):
            raise PermissionDenied("Apenas igrejas podem acessar este recurso.")
        if user and not is_active(user):
            raise PermissionDenied("Sua conta não está ativa.")
        return user

class MemberOnlyAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and not is_admin(user) and not is_member(user):
            raise PermissionDenied("Apenas membros podem acessar este recurso.")
        if user and not is_verified(user):
            raise PermissionDenied("Verifique seu e-mail para acessar.")
        return user


class AdminOnlyAuth(JWTAuth):
    """Autenticação que permite apenas Administradores."""
    
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and not is_admin(user):
            raise PermissionDenied("Apenas administradores podem acessar este recurso.")
        return user


class ActiveUserAuth(JWTAuth):
    """Autenticação que permite apenas usuários ativos (qualquer role)."""
    
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and not is_active(user):
            raise PermissionDenied("Sua conta não está ativa.")
        return user
class VerifiedUserAuth(JWTAuth):
    """Autenticação que permite apenas usuários verificados."""
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and not is_admin(user) and not is_verified(user):
            raise PermissionDenied("Verifique seu e-mail para acessar.")
        return user