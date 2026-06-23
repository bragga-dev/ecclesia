"""
Member Selectors — queries de leitura para Member e MemberAddress.
Nenhuma escrita acontece aqui.
"""
from typing import Optional
import uuid
from django.db.models import QuerySet, Q
from dizimus.apps.users.models.member import Member, MemberAddress
from dizimus.apps.community.models.member_church_model import MemberChurch

# ── Busca individual ──────────────────────────────────────────────────────────

def get_member_by_id(member_id: uuid.UUID) -> Optional[Member]:
    return Member.objects.filter(pk=member_id).first()


def get_member_by_user_id(user_id: uuid.UUID) -> Optional[Member]:
    return Member.objects.filter(user_id=user_id).first()


def get_member_by_slug(slug: str) -> Optional[Member]:
    return Member.objects.filter(slug=slug).first()


def get_member_by_username(username: str) -> Optional[Member]:
    return Member.objects.filter(username__iexact=username).first()


def get_member_by_cpf(cpf: str) -> Optional[Member]:
    return Member.objects.filter(cpf=cpf).first()

def get_member_church(member_id: uuid.UUID, church_id: uuid.UUID) -> MemberChurch:
    return MemberChurch.objects.get(member=member_id, church=church_id)


# ── Verificações de existência ────────────────────────────────────────────────

def member_exists(member_id: uuid.UUID) -> bool:
    return Member.objects.filter(pk=member_id).exists()


def username_exists(username: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    qs = Member.objects.filter(username__iexact=username)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


def cpf_exists(cpf: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    qs = Member.objects.filter(cpf=cpf)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()


# ── Listagens ─────────────────────────────────────────────────────────────────

def get_all_members() -> QuerySet[Member]:
    return Member.objects.all()


def get_members_excluding_id(member_id: uuid.UUID) -> QuerySet[Member]:
    return Member.objects.exclude(pk=member_id)


def get_members_ordered_by_name() -> QuerySet[Member]:
    return Member.objects.order_by("first_name", "last_name")


# ── Com select_related / prefetch ─────────────────────────────────────────────

def get_member_with_user(member_id: uuid.UUID) -> Optional[Member]:
    return (
        Member.objects
        .select_related("user")
        .filter(pk=member_id)
        .first()
    )


def get_member_with_addresses(member_id: uuid.UUID) -> Optional[Member]:
    return (
        Member.objects
        .prefetch_related("addresses")
        .filter(pk=member_id)
        .first()
    )


def get_member_full(member_id: uuid.UUID) -> Optional[Member]:
    return (
        Member.objects
        .select_related("user")
        .prefetch_related("addresses")
        .filter(pk=member_id)
        .first()
    )


# ── MemberAddress ─────────────────────────────────────────────────────────────

def get_addresses_by_member(member_id: uuid.UUID) -> QuerySet[MemberAddress]:
    return MemberAddress.objects.filter(member_id=member_id)


def get_member_principal_address(member_id: uuid.UUID) -> Optional[MemberAddress]:
    return MemberAddress.objects.filter(member_id=member_id, principal=True).first()


def get_member_address_by_id(address_id: uuid.UUID) -> Optional[MemberAddress]:
    return MemberAddress.objects.filter(pk=address_id).first()


def get_address_by_id_and_member(
    address_id: uuid.UUID,
    member_id: uuid.UUID,
) -> Optional[MemberAddress]:
    return MemberAddress.objects.filter(pk=address_id, member_id=member_id).first()


# ── Search ────────────────────────────────────────────────────────────────────
def search_members(search: str):
    search = search.strip()
    if not search:
        return Member.objects.none()
    return Member.objects.filter(
        Q(first_name__icontains=search) |
        Q(last_name__icontains=search) |
        Q(username__icontains=search) |
        Q(phone__icontains=search) |
        Q(cpf__icontains=search) |
        Q(addresses__city__icontains=search) |
        Q(addresses__state__icontains=search) |
        Q(addresses__cep__icontains=search) |
        Q(addresses__district__icontains=search)
    ).distinct()

def search_members_by_username(query: str) -> QuerySet[Member]:
    query = query.strip()
    if not query:
        return Member.objects.none()
    return Member.objects.filter(
        Q(username__icontains=query)
    ).distinct()


def search_members_by_city(city: str) -> QuerySet[Member]:
    city = city.strip()
    if not city:
        return Member.objects.none()
    return Member.objects.filter(
        addresses__city__icontains=city
    ).distinct()


def get_members_by_birth_month(month: int) -> QuerySet[Member]:
    return Member.objects.filter(date_of_birth__month=month)