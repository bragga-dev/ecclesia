"""
MemberChurch Selectors — queries de leitura para MemberChurch.
Nenhuma escrita acontece aqui.
"""
import uuid
from django.db.models import QuerySet, Q
from dizimus.apps.community.models.member_church_model import MemberChurch


# ── Busca individual ──────────────────────────────────────────────────────────

def get_member_church(member_id: uuid.UUID, church_id: uuid.UUID,) -> MemberChurch | None:
    """Retorna o vínculo entre um membro e uma igreja."""
    return MemberChurch.objects.filter(
        member_id=member_id,
        church_id=church_id,
    ).select_related("member", "church").first()


def get_member_church_by_id(membership_id: uuid.UUID,) -> MemberChurch | None:
    """Retorna um vínculo pelo seu ID."""
    return MemberChurch.objects.filter(
        pk=membership_id,
    ).select_related("member", "church").first()


# ── Listagens ─────────────────────────────────────────────────────────────────

def get_all_members_by_church_id(church_id: uuid.UUID,) -> QuerySet[MemberChurch]:
    """Retorna todos os vínculos de uma igreja."""
    return (
        MemberChurch.objects
        .filter(church_id=church_id)
        .select_related("member", "church")
        .order_by("-joined_at")
    )


def get_all_churches_by_member_id(member_id: uuid.UUID,) -> QuerySet[MemberChurch]:
    """Retorna todos os vínculos de um membro (igrejas que ele pertence)."""
    return (
        MemberChurch.objects
        .filter(member_id=member_id)
        .select_related("member", "church")
        .order_by("-joined_at")
    )


# ── Filtros ───────────────────────────────────────────────────────────────────

def filter_members_by_status(queryset: QuerySet[MemberChurch],  status:list[ str],) ->  QuerySet[MemberChurch]:
    """Filtra vínculos por status (ACTIVE, PENDING, INACTIVE)."""
    return queryset.filter(status=status)


def filter_members_by_roles(queryset: QuerySet[MemberChurch], roles: list[str],) -> QuerySet[MemberChurch]:
    """Filtra vínculos por uma lista de funções."""
    return queryset.filter(role__in=roles)


def filter_members_by_contribution(queryset: QuerySet[MemberChurch], contribution_types: list[str],) -> QuerySet[MemberChurch]:
    """Filtra vínculos por tipo de contribuição."""
    return queryset.filter(contribution_type__in=contribution_types)


def filter_members_by_joined_after(queryset: QuerySet[MemberChurch],  date,) -> QuerySet[MemberChurch]:
    """Filtra vínculos cujo ingresso foi após uma data."""
    return queryset.filter(joined_at__gte=date)


# ── Search ────────────────────────────────────────────────────────────────────

def search_members_in_church(queryset: QuerySet[MemberChurch],  query: str,) -> QuerySet[MemberChurch]:
    """
    Busca por nome ou email dentro de um queryset já filtrado por igreja.
    Encadeia com get_all_members_by_church_id antes de chamar.
    """
    query = query.strip()
    if not query:
        return queryset.none()
    return queryset.filter(
        Q(member__first_name__icontains=query) |
        Q(member__last_name__icontains=query) |
        Q(member__user__email__icontains=query) |
        Q(member__user__cpf__icontains=query)
    ).distinct()