"""
Schemas — Pydantic models para validação e serialização.
"""
# Users schemas (auth e user base)
from .users_schemas import (
    RegisterIn,
    LoginIn,
    TokenOut,
    RefreshIn,
    ChangePasswordIn,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    UserOut,
    UserUpdateIn,
    MessageOut,
)

# Profile schemas (Church e Member específicos + Address)
from .profile_schemas import (
    ChurchUpdateIn,
    ChurchProfileOut,
    MemberUpdateIn,
    MemberProfileOut,
    AddressIn,
    AddressUpdateIn,
    AddressOut,
)

__all__ = [
    # Auth
    "RegisterIn",
    "LoginIn",
    "TokenOut",
    "RefreshIn",
    "ChangePasswordIn",
    "PasswordResetRequestIn",
    "PasswordResetConfirmIn",
    # User
    "UserOut",
    "UserUpdateIn",
    # Profile
    "ChurchUpdateIn",
    "ChurchProfileOut",
    "MemberUpdateIn",
    "MemberProfileOut",
    # Address
    "AddressIn",
    "AddressUpdateIn",
    "AddressOut",
    # Generic
    "MessageOut",
]