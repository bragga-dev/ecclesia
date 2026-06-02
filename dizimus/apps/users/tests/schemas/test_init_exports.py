# test_init_exports.py

from dizimus.apps.users.schemas.church_schemas import ChurchUpdateIn
from dizimus.apps.users.schemas.users_schemas import UserOut, AddressIn, AddressOut
from dizimus.apps.users.schemas.member_schemas import MemberUpdateIn
from dizimus.apps.users.schemas.addresses_schemas import ChurchProfileOut, MemberProfileOut, AddressUpdateIn
from dizimus.apps.users.schemas.users_schemas import (
    UserOut,
    RegisterIn,
    LoginIn,
    TokenOut,
    RefreshIn,
    ChangePasswordIn,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    UserUpdateIn,
    MessageOut,
    # ← ChurchProfileOut and MemberProfileOut removed from here
)