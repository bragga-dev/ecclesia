"""
User Selectors — queries de leitura para User.
Nenhuma escrita acontece aqui.
"""
import uuid
from typing import Optional
from django.db.models import QuerySet, Q
from dizimus.apps.users.models import User
from  datetime import datetime

# ── Busca individual ──────────────────────────────────────────────────────────

def get_user_by_id(user_id: uuid.UUID) -> Optional[User]:
    """Busca usuário por ID."""
    return User.objects.filter(pk=user_id).first()


def get_user_by_email(email: str) -> Optional[User]:
    """Busca usuário por e-mail (case insensitive)."""
    return User.objects.filter(email__iexact=email).first()


def get_user_by_slug(slug: str) -> Optional[User]:
    """Busca usuário por slug."""
    return User.objects.filter(slug=slug).first()


# ── Verificações de existência ────────────────────────────────────────────────

def email_exists(email: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    """
    Verifica se e-mail já está em uso.
    Passa exclude_id para ignorar o próprio usuário em updates.
    """
    qs = User.objects.filter(email__iexact=email)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def user_exists(user_id: uuid.UUID) -> bool:
    """Verifica se usuário existe."""
    return User.objects.filter(pk=user_id).exists()


# ── Listagens ─────────────────────────────────────────────────────────────────

def get_all_users() -> QuerySet[User]:
    """Retorna todos os usuários."""
    return User.objects.all()


def get_active_users() -> QuerySet[User]:
    """Retorna usuários ativos."""
    return User.objects.filter(is_active=True)


def get_inactive_users() -> QuerySet[User]:
    """Retorna usuários inativados."""
    return User.objects.filter(is_active=False)


def get_users_by_role(role: str) -> QuerySet[User]:
    """Retorna usuários por role. Use as constantes: ROLE_MEMBER, ROLE_CHURCH, ROLE_ADMIN."""
    return User.objects.filter(role=role)


def get_trusty_users() -> QuerySet[User]:
    """Retorna usuários marcados como confiáveis."""
    return User.objects.filter(is_trusty=True)


def get_staff_users() -> QuerySet[User]:
    """Retorna usuários com acesso ao admin."""
    return User.objects.filter(is_staff=True)


# ── Exclusões ─────────────────────────────────────────────────────────────────

def get_users_excluding_id(user_id: uuid.UUID) -> QuerySet[User]:
    """Retorna todos os usuários exceto o informado."""
    return User.objects.exclude(pk=user_id)


def get_users_excluding_role(role: str) -> QuerySet[User]:
    """Retorna usuários que não possuem o role informado."""
    return User.objects.exclude(role=role)


# ── Ordenação ─────────────────────────────────────────────────────────────────

def get_users_ordered_by_date(descending: bool = True) -> QuerySet[User]:
    """Retorna usuários ordenados por data de cadastro."""
    order = "-date_joined" if descending else "date_joined"
    return User.objects.order_by(order)


# ── Combinados (uso comum em endpoints) ───────────────────────────────────────

def get_active_users_by_role(role: str) -> QuerySet[User]:
    """Retorna usuários ativos de um role específico."""
    return User.objects.filter(is_active=True, role=role)


def get_user_with_related(user_id: uuid.UUID) -> Optional[User]:
    """
    Busca usuário com select_related para church ou member.
    Evita N+1 quando você vai acessar user.church ou user.member logo depois.
    """
    return (
        User.objects
        .select_related("church", "member")
        .filter(pk=user_id)
        .first()
    )

# ── Search ────────────────────────────────────────────────────────────────────

def search_users(query: str) -> QuerySet[User]:
    """ Busca usuários por e-mail ou telefone.  """
    query = query.strip()
    if not query:
        return User.objects.none()
    return User.objects.filter(Q(email__icontains=query) | Q(phone__icontains=query)).distinct()


def search_users_by_role_and_status(role: str, is_active: bool) -> QuerySet[User]:
    """
    Filtra usuários por role e status.
    Ex: todos os membros ativos, todas as igrejas inativas.
    """
    return User.objects.filter(role=role, is_active=is_active)


def get_users_by_date_range(start: datetime, end: datetime) -> QuerySet[User]:
    """
    Usuários cadastrados num período — útil pra relatórios.
    """
    return User.objects.filter(date_joined__date__range=(start, end))

def search_users_by_role_and_status(role: str, is_active: bool) -> QuerySet[User]:
    """Ex: todos os membros ativos, todas as igrejas inativas."""

def get_users_by_date_range(start: datetime, end: datetime) -> QuerySet[User]:
    """Usuários cadastrados num período — útil pra relatórios."""

def search_users(query: str) -> QuerySet[User]:
    Q(email__icontains=query) | Q(phone__icontains=query)   