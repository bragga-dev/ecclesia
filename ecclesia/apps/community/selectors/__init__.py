# ── MemberChurch Selectors ────────────────────────────────────────────────────
from ecclesia.apps.community.selectors.member_church_selector import (
    get_member_church,
    get_member_church_by_id,
    get_all_members_by_church_id,
    get_all_churches_by_member_id,
    filter_members_by_status,
    filter_members_by_roles,
    filter_members_by_contribution,
    filter_members_by_joined_after,
    apply_member_filters,
    search_memberships_selector,
)

# ── ChurchAffiliationRequest Selectors ──────────────────────────────────────
from ecclesia.apps.community.selectors.church_in_church_selector import (
    # Busca individual
    get_all_affiliated_churches_by_id,
    get_affiliated_churche_by_id,
    
    # Filtros e busca
    amply_church_in_church_filters,
    search_church_in_church_selector,
    
    # Status
    get_pending_affiliation_requests,
    get_expired_affiliation_requests,
    get_active_affiliations,
    
    # Modo
    get_offline_invites_by_email,
    get_offline_invites_by_code,
    get_pending_offline_invites,
    
    # Tipo
    get_invites_sent_by_church,
    get_requests_received_by_church,
    
    # Relacionamento
    get_church_affiliation_network,
    get_church_affiliation_history,
    get_affiliations_between_churches,
    
    # Estatísticas
    get_affiliation_stats,
    get_church_affiliation_summary,
    
    # Validação (existentes)
    has_pending_affiliation_with_church,
    is_church_already_affiliated,
    validate_offline_invite_code,
    
    # Manutenção
    expire_pending_requests,
    get_requests_to_cleanup,
    
    # Otimizadas
    get_affiliation_requests_with_prefetch,

    
    validate_church_can_send_invite,
    validate_church_can_receive_invite,
    validate_church_can_request_affiliation,
    validate_church_can_be_requested,
    validate_no_self_affiliation,
    validate_no_existing_affiliation,
    validate_no_pending_affiliation,
    validate_offline_invite_email,
    validate_no_pending_offline_invite_for_email,
    validate_church_name_not_exists,
    validate_church_not_already_affiliated_by_name,
    validate_church_can_be_offline_invited,
    validate_church_can_authenticated_invite,
    validate_church_can_affiliation_request,
)


__all__ = [
    # MemberChurch
    "get_member_church",
    "get_member_church_by_id",
    "get_all_members_by_church_id",
    "get_all_churches_by_member_id",
    "filter_members_by_status",
    "filter_members_by_roles",
    "filter_members_by_contribution",
    "filter_members_by_joined_after",
    "apply_member_filters",
    "search_memberships_selector",

    # ChurchAffiliationRequest - Busca individual
    "get_all_affiliated_churches_by_id",
    "get_affiliated_churche_by_id",
    
    # ChurchAffiliationRequest - Filtros e busca
    "amply_church_in_church_filters",
    "search_church_in_church_selector",
    
    # ChurchAffiliationRequest - Status
    "get_pending_affiliation_requests",
    "get_expired_affiliation_requests",
    "get_active_affiliations",
    
    # ChurchAffiliationRequest - Modo
    "get_offline_invites_by_email",
    "get_offline_invites_by_code",
    "get_pending_offline_invites",
    
    # ChurchAffiliationRequest - Tipo
    "get_invites_sent_by_church",
    "get_requests_received_by_church",
    
    # ChurchAffiliationRequest - Relacionamento
    "get_church_affiliation_network",
    "get_church_affiliation_history",
    "get_affiliations_between_churches",
    
    # ChurchAffiliationRequest - Estatísticas
    "get_affiliation_stats",
    "get_church_affiliation_summary",
    
    # ChurchAffiliationRequest - Validação (existentes)
    "has_pending_affiliation_with_church",
    "is_church_already_affiliated",
    "validate_offline_invite_code",
    
    # ChurchAffiliationRequest - Manutenção
    "expire_pending_requests",
    "get_requests_to_cleanup",
    
    # ChurchAffiliationRequest - Otimizadas
    "get_affiliation_requests_with_prefetch",

    # ── NOVAS Validações de Negócio ──────────────────────────────────────
    "validate_church_can_send_invite",
    "validate_church_can_receive_invite",
    "validate_church_can_request_affiliation",
    "validate_church_can_be_requested",
    "validate_no_self_affiliation",
    "validate_no_existing_affiliation",
    "validate_no_pending_affiliation",
    "validate_offline_invite_email",
    "validate_no_pending_offline_invite_for_email",
    "validate_church_name_not_exists",
    "validate_church_not_already_affiliated_by_name",
    "validate_church_can_be_offline_invited",
    "validate_church_can_authenticated_invite",
    "validate_church_can_affiliation_request",
]