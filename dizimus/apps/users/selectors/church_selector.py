"""
Church Selectors — queries de leitura para Church e ChurchAddress.
Nenhuma escrita acontece aqui.
"""

from typing import Optional
import uuid
from django.db.models import QuerySet, Q
from dizimus.apps.users.models.church import Church
from dizimus.apps.users.models import Church, ChurchAddress


# ── Busca individual ──────────────────────────────────────────────────────────

def get_church_by_id(church_id: uuid.UUID) -> Optional[Church]:
    """Busca igreja por ID."""
    return Church.objects.filter(pk=church_id).first()


def get_church_by_user_id(user_id: uuid.UUID) -> Optional[Church]:
    """Busca igreja pelo ID do User vinculado."""
    return Church.objects.filter(user_id=user_id).first()


def get_church_by_slug(slug: str) -> Optional[Church]:
    """Busca igreja por slug."""
    return Church.objects.filter(slug=slug).first()


def get_church_by_cnpj(cnpj: str) -> Optional[Church]:
    """Busca igreja por CNPJ."""
    return Church.objects.filter(cnpj=cnpj).first()


# ── Verificações de existência ────────────────────────────────────────────────

def church_exists(church_id: uuid.UUID) -> bool:
    """Verifica se igreja existe."""
    return Church.objects.filter(pk=church_id).exists()


def cnpj_exists(cnpj: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    """
    Verifica se CNPJ já está em uso.
    Passa exclude_id para ignorar a própria igreja em updates.
    """
    qs = Church.objects.filter(cnpj=cnpj)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


# ── Listagens ─────────────────────────────────────────────────────────────────

def get_all_churches() -> QuerySet[Church]:
    """Retorna todas as igrejas."""
    return Church.objects.all()


def get_verified_churches() -> QuerySet[Church]:
    """Retorna igrejas verificadas."""
    return Church.objects.filter(is_verified=True)


def get_unverified_churches() -> QuerySet[Church]:
    """Retorna igrejas ainda não verificadas."""
    return Church.objects.filter(is_verified=False)


def get_churches_by_type(church_type: str) -> QuerySet[Church]:
    """
    Retorna igrejas por tipo.
    Use as constantes: Church.ChurchType.PARISH/COMMUNITY/INDEPENDENT
    """
    return Church.objects.filter(church_type=church_type)


def get_churches_by_parent(parent_id: uuid.UUID) -> QuerySet[Church]:
    """Retorna igrejas filhas de uma paróquia."""
    return Church.objects.filter(parent_church_id=parent_id)


def get_headquarters() -> QuerySet[Church]:
    """Retorna apenas sedes/matrizes."""
    return Church.objects.filter(church_type=Church.ChurchType.PARISH)


def get_churches_excluding_id(church_id: uuid.UUID) -> QuerySet[Church]:
    """Retorna todas as igrejas exceto a informada."""
    return Church.objects.exclude(pk=church_id)


def get_churches_ordered_by_name() -> QuerySet[Church]:
    """Retorna igrejas ordenadas por nome."""
    return Church.objects.order_by("full_name")


# ── Search ────────────────────────────────────────────────────────────────────

def search_churches(query: str) -> QuerySet[Church]:
    """
    Busca igrejas por nome, CNPJ ou cidade do endereço.
    Case insensitive. Retorna QuerySet vazio se query for blank.
    """
    query = query.strip()
    if not query:
        return Church.objects.none()

    return Church.objects.filter(
        Q(full_name__icontains=query) |
        Q(cnpj__icontains=query) |
        Q(addresses__city__icontains=query)
    ).distinct()


def search_verified_churches(query: str) -> QuerySet[Church]:
    """
    Busca igrejas verificadas por nome, CNPJ ou cidade.
    Útil para endpoints públicos.
    """
    query = query.strip()
    if not query:
        return Church.objects.none()

    return Church.objects.filter(
        is_verified=True
    ).filter(
        Q(full_name__icontains=query) |
        Q(cnpj__icontains=query) |
        Q(addresses__city__icontains=query)
    ).distinct()


# ── Com select_related / prefetch ─────────────────────────────────────────────

def get_church_with_user(church_id: uuid.UUID) -> Optional[Church]:
    """
    Busca igreja com select_related no User.
    Evita N+1 quando você vai acessar church.user logo depois.
    """
    return (
        Church.objects
        .select_related("user")
        .filter(pk=church_id)
        .first()
    )


def get_church_with_addresses(church_id: uuid.UUID) -> Optional[Church]:
    """
    Busca igreja com prefetch_related nos endereços.
    Evita N+1 quando você vai listar church.addresses.all() logo depois.
    """
    return (
        Church.objects
        .prefetch_related("addresses")
        .filter(pk=church_id)
        .first()
    )


def get_church_with_children(church_id: uuid.UUID) -> Optional[Church]:
    """
    Busca paróquia com prefetch das igrejas filhas.
    Útil para exibir a hierarquia de uma matriz.
    """
    return (
        Church.objects
        .prefetch_related("child_churches")
        .filter(pk=church_id)
        .first()
    )


def get_church_full(church_id: uuid.UUID) -> Optional[Church]:
    """
    Busca igreja com user, endereços e filhas — ideal para o endpoint /me.
    """
    return (
        Church.objects
        .select_related("user")
        .prefetch_related("addresses", "child_churches")
        .filter(pk=church_id)
        .first()
    )


# ── ChurchAddress ─────────────────────────────────────────────────────────────

def get_addresses_by_church(church_id: uuid.UUID) -> QuerySet[ChurchAddress]:
    """Retorna todos os endereços de uma igreja."""
    return ChurchAddress.objects.filter(church_id=church_id)


def get_church_principal_address(church_id: uuid.UUID) -> Optional[ChurchAddress]:
    """Retorna o endereço principal da igreja."""
    return ChurchAddress.objects.filter(church_id=church_id, principal=True).first()


def get_church_address_by_id(address_id: uuid.UUID) -> Optional[ChurchAddress]:
    """Busca endereço por ID."""
    return ChurchAddress.objects.filter(pk=address_id).first()


def get_address_by_id_and_church(address_id: uuid.UUID, church_id: uuid.UUID,) -> Optional[ChurchAddress]:
    """
    Busca endereço por ID garantindo que pertence à igreja.
    Use antes de qualquer update/delete de endereço.
    """
    return ChurchAddress.objects.filter(pk=address_id, church_id=church_id).first()


