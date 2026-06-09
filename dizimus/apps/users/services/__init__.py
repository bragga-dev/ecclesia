"""
Services — camada de lógica de negócio.
Orquestra selectors, repositories e tasks. Nunca acessa request.
"""

# ── Auth ────────────────────────────────────────────────────────────────
from .auth import login_user, logout_user, refresh_access_token, change_password
from .password_reset import request_password_reset, confirm_password_reset

# ── User ────────────────────────────────────────────────────────────────
from .user import register_user

# ── Profile (Member & Church) ───────────────────────────────────────────
from .profile import update_church_profile, update_member_profile
from .church_member import register_member_by_church

# # ── Church services ─────────────────────────────────────────────────────
# from dizimus.apps.users.services.church.church_service import (
#     create_church_profile_service,
#     get_church_profile_by_user,
#     get_church_profile_by_user_id,
#     get_church_profile_by_id,
#     get_church_profile_with_details,
#     get_church_profile_with_user,
#     get_church_profile_with_addresses,
#     get_church_profile_by_slug,
#     get_church_profile_by_cnpj,
#     church_profile_exists,
#     church_exists_by_user,
#     church_exists_by_id,
#     update_church_profile_service,
#     update_church_profile_by_id,
#     set_church_as_verified,
#     delete_church_profile,
#     delete_church_profile_by_id,
#     list_all_churches,
#     list_churches_by_type,
#     list_headquarters,
#     list_child_churches,
#     get_church_hierarchy,
#     validate_cnpj_uniqueness,
#     can_be_parent_church,
# )

# # ── Member services ─────────────────────────────────────────────────────
# from dizimus.apps.users.services.member.member_service import (
#     create_member_profile_service,
#     get_member_profile_by_user,
#     get_member_profile_by_user_id,
#     get_member_profile_by_id,
#     get_member_profile_by_username,
#     get_member_profile_by_cpf,
#     get_member_profile_by_slug,
#     get_member_profile_with_details,
#     get_member_profile_with_user,
#     get_member_profile_with_addresses,
#     member_profile_exists,
#     member_exists_by_user,
#     member_exists_by_id,
#     update_member_profile_service,
#     update_member_profile_by_id,
#     delete_member_profile,
#     delete_member_profile_by_id,
#     list_all_members,
#     list_members_by_contribution,
#     list_birthday_members,
#     list_members_by_name_order,
#     get_member_statistics,
#     validate_username_uniqueness,
#     validate_cpf_uniqueness,
#     is_birthday_today,
#     get_age,
# )

# ── Church Address services ─────────────────────────────────────────────
from dizimus.apps.users.services.church.church_address_service import (
    list_church_addresses,
    get_church_address_detail,
    get_church_principal_address_service,
    create_church_address_service,
    update_church_address_service,
    delete_church_address_service,
)

# ── Member Address services ─────────────────────────────────────────────
from dizimus.apps.users.services.member.member_address_service import (
    list_member_addresses,
    get_member_address_detail,
    get_member_principal_address_service,
    create_member_address_service,
    update_member_address_service,
    delete_member_address_service,
)

__all__ = [
    # Auth
    "login_user",
    "logout_user",
    "refresh_access_token",
    "change_password",
    "request_password_reset",
    "confirm_password_reset",

    # User
    "register_user",

    # Profile
    "update_church_profile",
    "update_member_profile",
    "register_member_by_church",

    # # Church
    # "create_church_profile_service",
    # "get_church_profile_by_user",
    # "get_church_profile_by_user_id",
    # "get_church_profile_by_id",
    # "get_church_profile_with_details",
    # "get_church_profile_with_user",
    # "get_church_profile_with_addresses",
    # "get_church_profile_by_slug",
    # "get_church_profile_by_cnpj",
    # "church_profile_exists",
    # "church_exists_by_user",
    # "church_exists_by_id",
    # "update_church_profile_service",
    # "update_church_profile_by_id",
    # "set_church_as_verified",
    # "delete_church_profile",
    # "delete_church_profile_by_id",
    # "list_all_churches",
    # "list_churches_by_type",
    # "list_headquarters",
    # "list_child_churches",
    # "get_church_hierarchy",
    # "validate_cnpj_uniqueness",
    # "can_be_parent_church",

    # # Member
    # "create_member_profile_service",
    # "get_member_profile_by_user",
    # "get_member_profile_by_user_id",
    # "get_member_profile_by_id",
    # "get_member_profile_by_username",
    # "get_member_profile_by_cpf",
    # "get_member_profile_by_slug",
    # "get_member_profile_with_details",
    # "get_member_profile_with_user",
    # "get_member_profile_with_addresses",
    # "member_profile_exists",
    # "member_exists_by_user",
    # "member_exists_by_id",
    # "update_member_profile_service",
    # "update_member_profile_by_id",
    # "delete_member_profile",
    # "delete_member_profile_by_id",
    # "list_all_members",
    # "list_members_by_contribution",
    # "list_birthday_members",
    # "list_members_by_name_order",
    # "get_member_statistics",
    # "validate_username_uniqueness",
    # "validate_cpf_uniqueness",
    # "is_birthday_today",
    # "get_age",

    # Church Address
    "list_church_addresses",
    "get_church_address_detail",
    "get_church_principal_address_service",
    "create_church_address_service",
    "update_church_address_service",
    "delete_church_address_service",

    # Member Address
    "list_member_addresses",
    "get_member_address_detail",
    "get_member_principal_address_service",
    "create_member_address_service",
    "update_member_address_service",
    "delete_member_address_service",
]