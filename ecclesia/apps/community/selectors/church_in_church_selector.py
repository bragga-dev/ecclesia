from django.db.models import QuerySet, Q
import uuid
from ecclesia.apps.community.schemas.church_in_church_schema import ChurchAffiliationRequestFilter
from ecclesia.apps.community.models import ChurchAffiliationRequest
from datetime import timezone, timedelta
from typing import Optional
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from ecclesia.apps.users.models.church import Church

# ── Busca individual ────────────────────────────────────────────────────────────────────


def get_all_affiliated_churches_by_id(church_in_church_id: uuid.UUID) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna todas as igrejas-comunidade afiliadas a uma igreja sede."""
    return (
        ChurchAffiliationRequest.objects
        .filter(church_in_church_id=church_in_church_id)
        .select_related("from_church", "to_church")
        .order_by("-created_at")
    )

def get_affiliated_churche_by_id(from_church_id: uuid.UUID, to_church_id: uuid.UUID) -> ChurchAffiliationRequest:
    """Retorna uma igreja-cominidade especifica de uma igreja sede pelo id"""
    return ChurchAffiliationRequest.objects.filter(
        from_church_id=from_church_id,
        to_church_id=to_church_id,
    ).select_related("from_church", "to_church").first()


# ── Filtros ────────────────────────────────────────────────────────────────────
def amply_church_in_church_filters(queryset: QuerySet[ChurchAffiliationRequest], filters: ChurchAffiliationRequestFilter):
    """
    Aplica filtros avançados na queryset de ChurchAffiliationRequest
    """
    if filters.status:
        queryset = queryset.filter(status__in=filters.status)

    if filters.request_type:
        queryset = queryset.filter(request_type__in=filters.request_type)
    
    if filters.created_after:
        queryset = queryset.filter(created_at__gte=filters.created_after)

    if filters.created_before:
        queryset = queryset.filter(created_at__lte=filters.created_before)

    if filters.church_id:
        queryset = queryset.filter(Q(from_church_id=filters.church_id) | Q(to_church_id=filters.church_id))
    
    if filters.expires_at:
        queryset = queryset.filter(expires_at__lte=filters.expires_at)

    return queryset.distinct()

# ── Search ────────────────────────────────────────────────────────────────────

def search_church_in_church_selector(queryset: QuerySet[ChurchAffiliationRequest], query: str) -> QuerySet[ChurchAffiliationRequest]:
    """
    Busca textual em ChurchAffiliationRequest
    """
    query = query.strip()
    if not query:
        return queryset
    
    return queryset.filter(
        Q(invited_church_full_name__icontains=query) |
        Q(invited_email__icontains=query) |
        Q(from_church__full_name__icontains=query) |
        Q(to_church__full_name__icontains=query) |
        Q(message__icontains=query) |
        Q(code__icontains=query)
    ).distinct()

# ── Queries por Status ──────────────────────────────────────────────────────

def get_pending_affiliation_requests(church_id: uuid.UUID, as_from: bool = True) -> QuerySet[ChurchAffiliationRequest]:
    """
    Retorna solicitações pendentes de uma igreja específica.
    as_from=True: solicitações ENVIADAS pela igreja
    as_from=False: solicitações RECEBIDAS pela igreja
    """
    filter_kwargs = {
        "status": ChurchAffiliationRequest.Status.PENDING,
        "expires_at__gt": timezone.now() if as_from else None
    }
    
    if as_from:
        filter_kwargs["from_church_id"] = church_id
    else:
        filter_kwargs["to_church_id"] = church_id
    
    return (
        ChurchAffiliationRequest.objects
        .filter(**filter_kwargs)
        .select_related("from_church", "to_church")
        .order_by("created_at")
    )


def get_expired_affiliation_requests(church_id: uuid.UUID) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna solicitações expiradas de uma igreja."""
    return (
        ChurchAffiliationRequest.objects
        .filter(
            Q(from_church_id=church_id) | Q(to_church_id=church_id),
            status=ChurchAffiliationRequest.Status.PENDING,
            expires_at__lt=timezone.now()
        )
        .select_related("from_church", "to_church")
        .order_by("-expires_at")
    )


def get_active_affiliations(church_id: uuid.UUID) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna afiliações ativas (aceitas) de uma igreja."""
    return (
        ChurchAffiliationRequest.objects
        .filter(Q(from_church_id=church_id) | Q(to_church_id=church_id), status=ChurchAffiliationRequest.Status.ACCEPTED)
        .select_related("from_church", "to_church")
        .order_by("-accepted_at")
    )

# ── Queries por Modo ────────────────────────────────────────────────────────

def get_offline_invites_by_email(email: str, status: Optional[list] = None) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna convites offline enviados para um email específico."""
    queryset = ChurchAffiliationRequest.objects.filter(
        mode=ChurchAffiliationRequest.Mode.OFFLINE,
        invited_email__iexact=email,
        request_type=ChurchAffiliationRequest.RequestType.INVITE
    )
    
    if status:
        queryset = queryset.filter(status__in=status)
    
    return queryset.select_related("from_church").order_by("-created_at")


def get_offline_invites_by_code(code: str) -> Optional[ChurchAffiliationRequest]:
    """Busca um convite offline pelo código."""
    try:
        return ChurchAffiliationRequest.objects.get(
            code=code,
            mode=ChurchAffiliationRequest.Mode.OFFLINE,
            status=ChurchAffiliationRequest.Status.PENDING
        )
    except ChurchAffiliationRequest.DoesNotExist:
        return None


def get_pending_offline_invites(church_id: uuid.UUID) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna convites offline pendentes de uma igreja."""
    return (
        ChurchAffiliationRequest.objects
        .filter(
            from_church_id=church_id,
            mode=ChurchAffiliationRequest.Mode.OFFLINE,
            status=ChurchAffiliationRequest.Status.PENDING,
            request_type=ChurchAffiliationRequest.RequestType.INVITE
        )
        .order_by("created_at")
    )

# ── Queries por Tipo ────────────────────────────────────────────────────────

def get_invites_sent_by_church(church_id: uuid.UUID, include_expired: bool = False) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna todos os convites enviados por uma igreja."""
    queryset = ChurchAffiliationRequest.objects.filter(
        from_church_id=church_id,
        request_type=ChurchAffiliationRequest.RequestType.INVITE
    )
    
    if not include_expired:
        queryset = queryset.exclude(
            status=ChurchAffiliationRequest.Status.EXPIRED
        )
    
    return queryset.select_related("to_church").order_by("-created_at")


def get_requests_received_by_church(church_id: uuid.UUID, include_expired: bool = False) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna todas as solicitações recebidas por uma igreja."""
    queryset = ChurchAffiliationRequest.objects.filter(
        to_church_id=church_id,
        request_type=ChurchAffiliationRequest.RequestType.REQUEST
    )
    
    if not include_expired:
        queryset = queryset.exclude(
            status=ChurchAffiliationRequest.Status.EXPIRED
        )
    
    return queryset.select_related("from_church").order_by("-created_at")


# ── Queries de Relacionamento ──────────────────────────────────────────────

def get_church_affiliation_network(church_id: uuid.UUID, max_depth: int = 2) -> QuerySet[ChurchAffiliationRequest]:
    """
    Retorna a rede de afiliação de uma igreja (até N níveis).
    Útil para visualizar a hierarquia de igrejas.
    """
    # Implementação básica - pode ser expandida para múltiplos níveis
    return (
        ChurchAffiliationRequest.objects
        .filter(
            Q(from_church_id=church_id) | Q(to_church_id=church_id),
            status=ChurchAffiliationRequest.Status.ACCEPTED
        )
        .select_related("from_church", "to_church")
    )


def get_church_affiliation_history(church_id: uuid.UUID, limit: int = 10) -> QuerySet[ChurchAffiliationRequest]:
    """Retorna o histórico de afiliações de uma igreja."""
    return (
        ChurchAffiliationRequest.objects
        .filter(
            Q(from_church_id=church_id) | Q(to_church_id=church_id)
        )
        .exclude(status=ChurchAffiliationRequest.Status.PENDING)
        .select_related("from_church", "to_church")
        .order_by("-created_at")[:limit]
    )


def get_affiliations_between_churches(church1_id: uuid.UUID, church2_id: uuid.UUID) -> Optional[ChurchAffiliationRequest]:
    """Retorna a relação de afiliação entre duas igrejas específicas."""
    return (
        ChurchAffiliationRequest.objects
        .filter(
            Q(
                from_church_id=church1_id,
                to_church_id=church2_id
            ) | Q(
                from_church_id=church2_id,
                to_church_id=church1_id
            ),
            status=ChurchAffiliationRequest.Status.ACCEPTED
        )
        .select_related("from_church", "to_church")
        .first()
    )

# ── Queries Estatísticas ────────────────────────────────────────────────────

from django.db.models import Count, Q
from django.utils import timezone

def get_affiliation_stats(
    church_id: uuid.UUID
) -> dict:
    """Retorna estatísticas de afiliação de uma igreja."""
    return ChurchAffiliationRequest.objects.filter(
        Q(from_church_id=church_id) | Q(to_church_id=church_id)
    ).aggregate(
        total_requests=Count("id"),
        pending_requests=Count(
            "id",
            filter=Q(status=ChurchAffiliationRequest.Status.PENDING)
        ),
        accepted_requests=Count(
            "id",
            filter=Q(status=ChurchAffiliationRequest.Status.ACCEPTED)
        ),
        rejected_requests=Count(
            "id",
            filter=Q(status=ChurchAffiliationRequest.Status.REJECTED)
        ),
        expired_requests=Count(
            "id",
            filter=Q(status=ChurchAffiliationRequest.Status.EXPIRED)
        ),
        requests_last_30_days=Count(
            "id",
            filter=Q(created_at__gte=timezone.now() - timedelta(days=30))
        )
    )


def get_church_affiliation_summary(
    church_id: uuid.UUID
) -> dict:
    """
    Resumo das afiliações de uma igreja.
    Retorna contagem de igrejas afiliadas como sede e como comunidade.
    """
    accepted_affiliations = ChurchAffiliationRequest.objects.filter(
        status=ChurchAffiliationRequest.Status.ACCEPTED
    )
    
    return {
        "as_parish": accepted_affiliations.filter(
            from_church_id=church_id
        ).count(),
        "as_community": accepted_affiliations.filter(
            to_church_id=church_id
        ).count(),
        "total": accepted_affiliations.filter(
            Q(from_church_id=church_id) | Q(to_church_id=church_id)
        ).count()
    }

# ── Queries de Validação ────────────────────────────────────────────────────

def has_pending_affiliation_with_church(
    from_church_id: uuid.UUID,
    to_church_id: uuid.UUID
) -> bool:
    """Verifica se já existe uma solicitação pendente entre duas igrejas."""
    return ChurchAffiliationRequest.objects.filter(
        from_church_id=from_church_id,
        to_church_id=to_church_id,
        status=ChurchAffiliationRequest.Status.PENDING
    ).exists()


def is_church_already_affiliated(from_church_id: uuid.UUID, to_church_id: uuid.UUID) -> bool:
    """Verifica se duas igrejas já são afiliadas."""
    return ChurchAffiliationRequest.objects.filter(
        Q(
            from_church_id=from_church_id,
            to_church_id=to_church_id
        ) | Q(
            from_church_id=to_church_id,
            to_church_id=from_church_id
        ),
        status=ChurchAffiliationRequest.Status.ACCEPTED
    ).exists()


def validate_offline_invite_code(
    code: str,
    email: str
) -> Optional[ChurchAffiliationRequest]:
    """Valida se um código de convite offline é válido para um email."""
    try:
        return ChurchAffiliationRequest.objects.get(
            code=code,
            invited_email__iexact=email,
            mode=ChurchAffiliationRequest.Mode.OFFLINE,
            status=ChurchAffiliationRequest.Status.PENDING,
            expires_at__gt=timezone.now()
        )
    except ChurchAffiliationRequest.DoesNotExist:
        return None
    

# ── Queries de Manutenção ──────────────────────────────────────────────────

def expire_pending_requests() -> int:
    """
    Atualiza solicitações pendentes expiradas para status EXPIRED.
    Retorna o número de solicitações atualizadas.
    """
    expired_count = ChurchAffiliationRequest.objects.filter(
        status=ChurchAffiliationRequest.Status.PENDING,
        expires_at__lt=timezone.now(),
        mode=ChurchAffiliationRequest.Mode.OFFLINE
    ).update(status=ChurchAffiliationRequest.Status.EXPIRED)
    
    return expired_count


def get_requests_to_cleanup(days: int = 90) -> QuerySet[ChurchAffiliationRequest]:
    """
    Retorna solicitações antigas que podem ser arquivadas/removidas.
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    return ChurchAffiliationRequest.objects.filter(
        Q(status=ChurchAffiliationRequest.Status.EXPIRED) |
        Q(status=ChurchAffiliationRequest.Status.REJECTED) |
        Q(status=ChurchAffiliationRequest.Status.CANCELED),
        created_at__lt=cutoff_date
    )


# ── Queries Otimizadas ─────────────────────────────────────────────────────

def get_affiliation_requests_with_prefetch(
    church_id: uuid.UUID,
    **filters
) -> QuerySet[ChurchAffiliationRequest]:
    """
    Retorna solicitações com todos os dados relacionados pré-carregados.
    Otimizado para listagens com muitos dados.
    """
    return (
        ChurchAffiliationRequest.objects
        .filter(
            Q(from_church_id=church_id) | Q(to_church_id=church_id),
            **filters
        )
        .select_related(
            "from_church",
            "from_church__user",
            "to_church",
            "to_church__user"
        )
        .prefetch_related(
            "from_church__addresses",
            "to_church__addresses"
        )
        .only(
            "id",
            "request_type",
            "status",
            "mode",
            "code",
            "message",
            "created_at",
            "accepted_at",
            "expires_at",
            "from_church__full_name",
            "from_church__slug",
            "to_church__full_name",
            "to_church__slug",
            "invited_email",
            "invited_church_full_name"
        )
        .order_by("-created_at")
    )

# ── Validações de Negócio ──────────────────────────────────────────────────

def validate_church_can_send_invite(church: Church) -> None:
    """
    Valida se uma igreja pode enviar convites.
    Apenas igrejas Paróquia ativas podem enviar convites.
    """
    if church.church_type != Church.ChurchType.PARISH:
        raise ValidationError("Apenas Igrejas Paróquia podem enviar convites.")
    
    if not church.user.is_active:
        raise ValidationError("Não é possível enviar convite de uma igreja inativa.")


def validate_church_can_receive_invite(church: Church) -> None:
    """
    Valida se uma igreja pode receber convites.
    Apenas igrejas COMUNIDADE ativas podem receber convites.
    """
    if church.church_type != Church.ChurchType.COMMUNITY:
        raise ValidationError("Só é possível convidar igrejas do tipo Comunidade.")
    
    if not church.user.is_active:
        raise ValidationError("Não é possível enviar convite para uma igreja inativa.")


def validate_church_can_request_affiliation(church: Church) -> None:
    """
    Valida se uma igreja pode solicitar afiliação.
    Apenas igrejas COMUNIDADE ativas podem solicitar afiliação.
    """
    if church.church_type != Church.ChurchType.COMMUNITY:
        raise ValidationError("Apenas igrejas do tipo Comunidade podem solicitar afiliação.")
    
    if not church.user.is_active:
        raise ValidationError("Não é possível enviar solicitação de uma igreja inativa.")


def validate_church_can_be_requested(church: Church) -> None:
    """
    Valida se uma igreja pode receber solicitação de afiliação.
    Apenas igrejas Paróquia ativas podem receber solicitações.
    """
    if church.church_type != Church.ChurchType.PARISH:
        raise ValidationError("Uma Comunidade só pode se afiliar a uma Igreja Paróquia.")
    
    if not church.user.is_active:
        raise ValidationError("Não é possível solicitar afiliação a uma igreja inativa.")


def validate_no_self_affiliation(from_church_id: uuid.UUID, to_church_id: uuid.UUID) -> None:
    """Valida se uma igreja não está tentando se afiliar a si mesma."""
    if from_church_id == to_church_id:
        raise ValidationError("Uma igreja não pode enviar uma solicitação para si mesma.")


def validate_no_existing_affiliation(from_church_id: uuid.UUID, to_church_id: uuid.UUID) -> None:
    """Valida se não existe afiliação ativa entre as igrejas."""
    if is_church_already_affiliated(from_church_id, to_church_id):
        raise ValidationError("As igrejas já possuem uma afiliação ativa.")


def validate_no_pending_affiliation(from_church_id: uuid.UUID, to_church_id: uuid.UUID) -> None:
    """Valida se não existe solicitação pendente em nenhum dos sentidos."""
    if has_pending_affiliation_with_church(from_church_id, to_church_id):
        raise ValidationError("Já existe uma solicitação pendente entre estas igrejas.")
    
    if has_pending_affiliation_with_church(to_church_id, from_church_id):
        raise ValidationError("A igreja destino já possui uma solicitação pendente para a igreja origem.")


def validate_offline_invite_email(email: str) -> None:
    """Valida se o email é válido."""
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Email inválido!")


def validate_no_pending_offline_invite_for_email(email: str) -> None:
    """Valida se não existe convite offline pendente para este email."""
    if ChurchAffiliationRequest.objects.filter(
        invited_email__iexact=email,
        mode=ChurchAffiliationRequest.Mode.OFFLINE,
        status=ChurchAffiliationRequest.Status.PENDING
    ).exists():
        raise ValidationError("Já existe um convite pendente para este email.")


def validate_church_name_not_exists(full_name: str) -> None:
    """Valida se já não existe uma igreja com este nome."""
    if Church.objects.filter(full_name__iexact=full_name).exists():
        raise ValidationError("Já existe uma igreja cadastrada com este nome.")


def validate_church_not_already_affiliated_by_name(from_church: Church, full_name: str) -> None:
    """
    Valida se uma igreja com este nome já não está afiliada à from_church.
    """
    existing_church = Church.objects.filter(full_name__iexact=full_name).first()
    if existing_church:
        if is_church_already_affiliated(from_church.id, existing_church.id):
            raise ValidationError("Esta igreja já está afiliada.")
        if has_pending_affiliation_with_church(from_church.id, existing_church.id):
            raise ValidationError("Já existe uma solicitação pendente para esta igreja.")


def validate_church_can_be_offline_invited(from_church: Church, invited_email: str, invited_church_full_name: str) -> None:
    """
    Validação completa para convite offline.
    """
    validate_church_can_send_invite(from_church)
    validate_offline_invite_email(invited_email)
    validate_no_pending_offline_invite_for_email(invited_email)
    validate_church_name_not_exists(invited_church_full_name)
    validate_church_not_already_affiliated_by_name(from_church, invited_church_full_name)


def validate_church_can_authenticated_invite(from_church: Church, to_church: Church) -> None:
    """
    Validação completa para convite autenticado.
    """
    validate_no_self_affiliation(from_church.id, to_church.id)
    validate_church_can_send_invite(from_church)
    validate_church_can_receive_invite(to_church)
    validate_no_existing_affiliation(from_church.id, to_church.id)
    validate_no_pending_affiliation(from_church.id, to_church.id)


def validate_church_can_affiliation_request(from_church: Church, to_church: Church) -> None:
    """
    Validação completa para solicitação de afiliação.
    """
    validate_no_self_affiliation(from_church.id, to_church.id)
    validate_church_can_request_affiliation(from_church)
    validate_church_can_be_requested(to_church)
    validate_no_existing_affiliation(from_church.id, to_church.id)
    validate_no_pending_affiliation(from_church.id, to_church.id)

def get_church_affiliation_request_by_id(affiliation_id: uuid.UUID) -> ChurchAffiliationRequest | None:
    return (
        ChurchAffiliationRequest.objects
        .select_related(
            "from_church",
            "from_church__user",
            "to_church",
            "to_church__user",
        )
        .filter(id=affiliation_id)
        .first()
    )