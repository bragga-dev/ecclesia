"""
MemberChurch Selectors — queries de leitura para MemberChurch.
Nenhuma escrita acontece aqui.
"""
import uuid
from django.db.models import QuerySet, Q
from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.community.schemas.member_church_schema import ChurchMemberFilterIn

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


def apply_member_filters(queryset: QuerySet[MemberChurch], filters: ChurchMemberFilterIn,):

    if filters.status:
        queryset = queryset.filter(status__in=filters.status)

    if filters.roles:
        queryset = queryset.filter(role__in=filters.roles)

    if filters.contribution_types:
        queryset = queryset.filter(contribution_type__in=filters.contribution_types)

    if filters.joined_after:
        queryset = queryset.filter(joined_at__date__gte=filters.joined_after)

    if filters.joined_before:
        queryset = queryset.filter(joined_at__date__lte=filters.joined_before)

    if filters.first_name:
        queryset = queryset.filter(member__first_name__icontains=filters.first_name)

    if filters.last_name:
        queryset = queryset.filter(member__last_name__icontains=filters.last_name)

    if filters.username:
        queryset = queryset.filter(member__username__icontains=filters.username)

    if filters.email:
        queryset = queryset.filter(member__user__email__icontains=filters.email)

    if filters.cpf:
        queryset = queryset.filter(member__cpf__icontains=filters.cpf)

    if filters.phone:
        queryset = queryset.filter(member__phone__icontains=filters.phone)

    if filters.city:
        queryset = queryset.filter(member__addresses__city__icontains=filters.city)

    if filters.state:
        queryset = queryset.filter(member__addresses__state__icontains=filters.state)

    if filters.district:
        queryset = queryset.filter(member__addresses__district__icontains=filters.district)

    if filters.cep:
        queryset = queryset.filter(member__addresses__cep__icontains=filters.cep)

    if filters.has_phone is True:
        queryset = queryset.exclude(member__phone__isnull=True)

    if filters.has_cpf is True:
        queryset = queryset.exclude(member__cpf__isnull=True)

    return queryset.distinct()

# ── Search ────────────────────────────────────────────────────────────────────
def search_memberships_selector(queryset: QuerySet[MemberChurch], query: str,) -> QuerySet[MemberChurch]:
    query = query.strip()
    if not query:
        return queryset
    return (
        queryset
        .filter(

            # MEMBER
            Q(member__first_name__icontains=query)
            |
            Q(member__last_name__icontains=query)
            |
            Q(member__username__icontains=query)
            |
            Q(member__cpf__icontains=query)
            |
            Q(member__phone__icontains=query)
            |
            Q(member__user__email__icontains=query)

            # ADDRESS
            |
            Q(member__addresses__city__icontains=query)
            |
            Q(member__addresses__state__icontains=query)
            |
            Q(member__addresses__district__icontains=query)

            # MEMBER CHURCH
            |
            Q(role__icontains=query)
            |
            Q(status__icontains=query)
            |
            Q(contribution_type__icontains=query)

        )
        .distinct()
    )