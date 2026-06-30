# test_init_exports.py

from ecclesia.apps.users.schemas import (
    RegisterIn,
    LoginIn,
    TokenOut,
    RefreshIn,
    ChangePasswordIn,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    UserOut,
    MessageOut,
    ChurchProfileOut,
    MemberProfileOut,
    ChurchOut,
    ChurchCreateIn,
    ChurchUpdateIn,
    MemberOut,
    MemberCreateIn,
    MemberUpdateIn,
    AddressIn,
    AddressUpdateIn,
    AddressOut,
)


class TestInitExports:
    """Testa que todos os schemas estão sendo exportados corretamente"""

    def test_auth_schemas_exported(self):
        assert RegisterIn is not None
        assert LoginIn is not None
        assert TokenOut is not None
        assert RefreshIn is not None
        assert ChangePasswordIn is not None
        assert PasswordResetRequestIn is not None
        assert PasswordResetConfirmIn is not None

    def test_user_schemas_exported(self):
        assert UserOut is not None
        assert MessageOut is not None

    def test_profile_schemas_exported(self):
        assert ChurchProfileOut is not None
        assert MemberProfileOut is not None

    def test_church_schemas_exported(self):
        assert ChurchOut is not None
        assert ChurchCreateIn is not None
        assert ChurchUpdateIn is not None

    def test_member_schemas_exported(self):
        assert MemberOut is not None
        assert MemberCreateIn is not None
        assert MemberUpdateIn is not None

    def test_address_schemas_exported(self):
        assert AddressIn is not None
        assert AddressUpdateIn is not None
        assert AddressOut is not None