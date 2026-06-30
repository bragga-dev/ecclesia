"""
Schemas — Pydantic models para validação e serialização.
"""
from ecclesia.apps.users.schemas.users_schemas import (
    RegisterIn,
    LoginIn,
    TokenOut,
    RefreshIn,
    ChangePasswordIn,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    UserOut,
    MessageOut,
)
from ecclesia.apps.users.schemas.addresses_schemas import (
    AddressIn,
    AddressUpdateIn,
    AddressOut,
)
from ecclesia.apps.users.schemas.profile_church_schema import ChurchProfileOut
from ecclesia.apps.users.schemas.profile_member_schema import MemberProfileOut
from ecclesia.apps.users.schemas.member_schemas import (
    MemberOut,
    MemberCreateIn,
    MemberUpdateIn,
)
from ecclesia.apps.users.schemas.church_schemas import (
    ChurchOut,
    ChurchCreateIn,
    ChurchUpdateIn,
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
    # Profile
    "ChurchProfileOut",
    "MemberProfileOut",
    # Church
    "ChurchOut",
    "ChurchCreateIn",
    "ChurchUpdateIn",
    # Member
    "MemberOut",
    "MemberCreateIn",
    "MemberUpdateIn",
    # Address
    "AddressIn",
    "AddressUpdateIn",
    "AddressOut",
    # Generic
    "MessageOut",
]