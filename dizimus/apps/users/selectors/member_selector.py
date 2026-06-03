"""
Member Selectors — queries de leitura para Member e MemberAddress.
Nenhuma escrita acontece aqui.
"""
from typing import Optional
import uuid
from django.db.models import QuerySet, Q
from dizimus.apps.users.models.member import Member, MemberAddress


# ── Busca individual ──────────────────────────────────────────────────────────

def get_member_by_id(member_id: uuid.UUID) -> Optional[Member]:
    """Busca membro por ID."""
    return Member.objects.filter(pk=member_id).first()


def get_member_by_user_id(user_id: uuid.UUID) -> Optional[Member]:
    """Busca membro pelo ID do User vinculado."""
    return Member.objects.filter(user_id=user_id).first()


def get_member_by_slug(slug: str) -> Optional[Member]:
    """Busca membro por slug."""
    return Member.objects.filter(slug=slug).first()


def get_member_by_username(username: str) -> Optional[Member]:
    """Busca membro por username (case insensitive)."""
    return Member.objects.filter(username__iexact=username).first()


def get_member_by_cpf(cpf: str) -> Optional[Member]:
    """Busca membro por CPF."""
    return Member.objects.filter(cpf=cpf).first()


# ── Verificações de existência ────────────────────────────────────────────────

def member_exists(member_id: uuid.UUID) -> bool:
    """Verifica se membro existe."""
    return Member.objects.filter(pk=member_id).exists()


def username_exists(username: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    """
    Verifica se username já está em uso.
    Passa exclude_id para ignorar o próprio membro em updates.
    """
    qs = Member.objects.filter(username__iexact=username)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def cpf_exists(cpf: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    """
    Verifica se CPF já está em uso.
    Passa exclude_id para ignorar o próprio membro em updates.
    """
    qs = Member.objects.filter(cpf=cpf)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


# ── Listagens ─────────────────────────────────────────────────────────────────

def get_all_members() -> QuerySet[Member]:
    """Retorna todos os membros."""
    return Member.objects.all()


def get_members_by_contribution(contribution_type: str) -> QuerySet[Member]:
    """
    Retorna membros por tipo de contribuição.
    Use as constantes: Member.ContributionType.NONE/DIZIMISTA/OFERTANTE/BOTH
    """
    return Member.objects.filter(contribution_type=contribution_type)


def get_members_excluding_id(member_id: uuid.UUID) -> QuerySet[Member]:
    """Retorna todos os membros exceto o informado."""
    return Member.objects.exclude(pk=member_id)


def get_members_ordered_by_name() -> QuerySet[Member]:
    """Retorna membros ordenados por primeiro nome."""
    return Member.objects.order_by("first_name", "last_name")


# ── Com select_related / prefetch ─────────────────────────────────────────────

def get_member_with_user(member_id: uuid.UUID) -> Optional[Member]:
    """
    Busca membro com select_related no User.
    Evita N+1 quando você vai acessar member.user logo depois.
    """
    return (
        Member.objects
        .select_related("user")
        .filter(pk=member_id)
        .first()
    )


def get_member_with_addresses(member_id: uuid.UUID) -> Optional[Member]:
    """
    Busca membro com prefetch_related nos endereços.
    Evita N+1 quando você vai listar member.addresses.all() logo depois.
    """
    return (
        Member.objects
        .prefetch_related("addresses")
        .filter(pk=member_id)
        .first()
    )


def get_member_full(member_id: uuid.UUID) -> Optional[Member]:
    """
    Busca membro com user e endereços — ideal para o endpoint /me.
    """
    return (
        Member.objects
        .select_related("user")
        .prefetch_related("addresses")
        .filter(pk=member_id)
        .first()
    )


# ── MemberAddress ─────────────────────────────────────────────────────────────

def get_addresses_by_member(member_id: uuid.UUID) -> QuerySet[MemberAddress]:
    """Retorna todos os endereços de um membro."""
    return MemberAddress.objects.filter(member_id=member_id)


def get_principal_address(member_id: uuid.UUID) -> Optional[MemberAddress]:
    """Retorna o endereço principal do membro."""
    return MemberAddress.objects.filter(member_id=member_id, principal=True).first()


def get_address_by_id(address_id: uuid.UUID) -> Optional[MemberAddress]:
    """Busca endereço por ID."""
    return MemberAddress.objects.filter(pk=address_id).first()


def get_address_by_id_and_member(
    address_id: uuid.UUID,
    member_id: uuid.UUID,
) -> Optional[MemberAddress]:
    """
    Busca endereço por ID garantindo que pertence ao membro.
    Use antes de qualquer update/delete de endereço.
    """
    return MemberAddress.objects.filter(pk=address_id, member_id=member_id).first()


# ── Search ────────────────────────────────────────────────────────────────────

def search_members(query: str) -> QuerySet[Member]:
    """
    Busca membros por nome ou CPF.
    Case insensitive. Retorna QuerySet vazio se query for blank.
    """
    query = query.strip()
    if not query:
        return Member.objects.none()
    return Member.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(cpf__icontains=query)
    ).distinct()


def search_members_by_username(query: str) -> QuerySet[Member]:
    """Busca membros por username."""
    query = query.strip()
    if not query:
        return Member.objects.none()
    return Member.objects.filter(
        Q(username__icontains=query)
    ).distinct()


def search_members_by_contribution(query: str, contribution_type: str) -> QuerySet[Member]:
    """Busca membros por nome/CPF dentro de um tipo de contribuição específico."""
    query = query.strip()
    if not query:
        return Member.objects.none()
    return Member.objects.filter(
        contribution_type=contribution_type
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(cpf__icontains=query)
    ).distinct()


def search_members_by_city(city: str) -> QuerySet[Member]:
    """Busca membros pela cidade do endereço."""
    city = city.strip()
    if not city:
        return Member.objects.none()
    return Member.objects.filter(
        addresses__city__icontains=city
    ).distinct()


def get_members_by_birth_month(month: int) -> QuerySet[Member]:
    """
    Retorna membros aniversariantes do mês informado.
    Ex: get_members_by_birth_month(6) → aniversariantes de junho.
    """
    return Member.objects.filter(date_of_birth__month=month)


