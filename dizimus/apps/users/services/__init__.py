"""
Services — regras de negócio.
Orquestra selectors, repositories e tasks. Nunca acessa request.
"""
from .auth import login_user, logout_user, refresh_access_token, change_password
from .password_reset import request_password_reset, confirm_password_reset
from .user import register_user, update_user_profile
from .profile import update_church_profile, update_member_profile
from .address import (
    list_my_addresses,
    create_my_address,
    update_my_address,
    delete_my_address,
)

__all__ = [
    # Auth
    "login_user",
    "logout_user",
    "refresh_access_token",
    "change_password",
    # Password Reset
    "request_password_reset",
    "confirm_password_reset",
    # User
    "register_user",
    "update_user_profile",
    # Profile
    "update_church_profile",
    "update_member_profile",
    # Address
    "list_my_addresses",
    "create_my_address",
    "update_my_address",
    "delete_my_address",
]