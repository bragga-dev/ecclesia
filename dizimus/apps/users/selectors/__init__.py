"""
Selectors — apenas leitura do banco.
Nenhuma escrita acontece aqui.
"""

# ── User ──────────────────────────────────────────────────────────────────────
from .user import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_slug,
    email_exists,
    user_exists,
    get_all_users,
    get_active_users,
    get_inactive_users,
    get_users_by_role,
    get_trusty_users,
    get_staff_users,
    get_users_excluding_id,
    get_users_excluding_role,
    get_users_ordered_by_date,
    get_active_users_by_role,
    get_user_with_related,
    search_users,
    search_users_by_role_and_status,
    get_users_by_date_range,
)

# ── Member ────────────────────────────────────────────────────────────────────
from .member_selector import (
    get_member_by_id,
    get_member_by_user_id,
    get_member_by_slug,
    get_member_by_username,
    get_member_by_cpf,
    member_exists,
    username_exists,
    cpf_exists,
    get_all_members,
    get_members_by_contribution,
    get_members_excluding_id,
    get_members_ordered_by_name,
    get_member_with_user,
    get_member_with_addresses,
    get_member_full,
    get_addresses_by_member,
    get_member_principal_address,
    get_member_address_by_id,
    get_address_by_id_and_member,
    search_members,
    search_members_by_username,
    search_members_by_contribution,
    search_members_by_city,
    get_members_by_birth_month,
)

# ── Church ────────────────────────────────────────────────────────────────────
from .church_selector import (
    get_church_by_id,
    get_church_by_user_id,
    get_church_by_slug,
    get_church_by_cnpj,
    church_exists,
    cnpj_exists,
    get_all_churches,
    get_verified_churches,
    get_unverified_churches,
    get_churches_by_type,
    get_churches_by_parent,
    get_headquarters,
    get_churches_excluding_id,
    get_churches_ordered_by_name,
    get_church_with_user,
    get_church_with_addresses,
    get_church_with_children,
    get_church_full,
    get_addresses_by_church,
    get_church_principal_address,
    get_church_address_by_id,
    get_address_by_id_and_church,
    search_churches,
    search_verified_churches,
)

__all__ = [
    # User — busca
    "get_user_by_id",
    "get_user_by_email",
    "get_user_by_slug",
    # User — existência
    "email_exists",
    "user_exists",
    # User — listagens
    "get_all_users",
    "get_active_users",
    "get_inactive_users",
    "get_users_by_role",
    "get_trusty_users",
    "get_staff_users",
    "get_users_excluding_id",
    "get_users_excluding_role",
    "get_users_ordered_by_date",
    "get_active_users_by_role",
    "get_user_with_related",
    # User — search
    "search_users",
    "search_users_by_role_and_status",
    "get_users_by_date_range",

    # Member — busca
    "get_member_by_id",
    "get_member_by_user_id",
    "get_member_by_slug",
    "get_member_by_username",
    "get_member_by_cpf",
    # Member — existência
    "member_exists",
    "username_exists",
    "cpf_exists",
    # Member — listagens
    "get_all_members",
    "get_members_by_contribution",
    "get_members_excluding_id",
    "get_members_ordered_by_name",
    "get_member_with_user",
    "get_member_with_addresses",
    "get_member_full",
    # Member — endereços
    "get_addresses_by_member",
    "get_member_principal_address",
    "get_member_address_by_id",
    "get_address_by_id_and_member",
    # Member — search
    "search_members",
    "search_members_by_username",
    "search_members_by_contribution",
    "search_members_by_city",
    "get_members_by_birth_month",

    # Church — busca
    "get_church_by_id",
    "get_church_by_user_id",
    "get_church_by_slug",
    "get_church_by_cnpj",
    # Church — existência
    "church_exists",
    "cnpj_exists",
    # Church — listagens
    "get_all_churches",
    "get_verified_churches",
    "get_unverified_churches",
    "get_churches_by_type",
    "get_churches_by_parent",
    "get_headquarters",
    "get_churches_excluding_id",
    "get_churches_ordered_by_name",
    "get_church_with_user",
    "get_church_with_addresses",
    "get_church_with_children",
    "get_church_full",
    # Church — endereços
    "get_addresses_by_church",
    "get_church_principal_address",
    "get_church_address_by_id",
    "get_address_by_id_and_church",
    # Church — search
    "search_churches",
    "search_verified_churches",
]