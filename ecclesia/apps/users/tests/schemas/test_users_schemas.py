# ecclesia/apps/users/tests/schemas/test_users_schemas.py

import pytest
from datetime import datetime
from pydantic import ValidationError
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
    UserRoleEnum,
)
from ecclesia.apps.users.models import User


class TestRegisterIn:
    """Testes do schema de registro"""

    def test_valid_member_registration(self):
        data = {
            "email": "joao@teste.com",
            "password": "SenhaForte123!",
            "password2": "SenhaForte123!",
            "role": UserRoleEnum.MEMBER,
        }
        schema = RegisterIn(**data)
        assert schema.email == "joao@teste.com"
        assert schema.role == UserRoleEnum.MEMBER

    def test_valid_church_registration(self):
        data = {
            "email": "contato@igreja.com",
            "password": "SenhaForte123!",
            "password2": "SenhaForte123!",
            "role": UserRoleEnum.CHURCH,
        }
        schema = RegisterIn(**data)
        assert schema.role == UserRoleEnum.CHURCH

    def test_passwords_must_match(self):
        data = {
            "email": "joao@teste.com",
            "password": "SenhaForte123!",
            "password2": "SenhaDiferente456!",
            "role": UserRoleEnum.MEMBER,
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterIn(**data)
        assert "senhas não coincidem" in str(exc_info.value).lower()

    def test_weak_password_raises_error(self):
        data = {
            "email": "joao@teste.com",
            "password": "123",
            "password2": "123",
            "role": UserRoleEnum.MEMBER,
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterIn(**data)
        assert "password" in str(exc_info.value).lower()

    def test_invalid_email_format(self):
        data = {
            "email": "email_invalido",
            "password": "SenhaForte123!",
            "password2": "SenhaForte123!",
            "role": UserRoleEnum.MEMBER,
        }
        with pytest.raises(ValidationError):
            RegisterIn(**data)

    def test_password_too_short(self):
        data = {
            "email": "joao@teste.com",
            "password": "1234567",
            "password2": "1234567",
            "role": UserRoleEnum.MEMBER,
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterIn(**data)
        assert "String should have at least 8 characters" in str(exc_info.value)


class TestLoginIn:
    """Testes do schema de login"""

    def test_valid_login_data(self):
        data = {"email": "user@teste.com", "password": "senha123"}
        schema = LoginIn(**data)
        assert schema.email == "user@teste.com"
        assert schema.password == "senha123"


class TestTokenOut:
    """Testes do schema de token"""

    def test_token_output(self):
        data = {"access": "token_access_123", "refresh": "token_refresh_456"}
        schema = TokenOut(**data)
        assert schema.access == "token_access_123"
        assert schema.refresh == "token_refresh_456"


class TestRefreshIn:
    """Testes do schema de refresh token"""

    def test_refresh_input(self):
        data = {"refresh": "refresh_token_123"}
        schema = RefreshIn(**data)
        assert schema.refresh == "refresh_token_123"


class TestChangePasswordIn:
    """Testes do schema de alteração de senha"""

    def test_valid_password_change(self):
        data = {
            "old_password": "SenhaAntiga123!",
            "new_password": "SenhaNova456!",
            "new_password2": "SenhaNova456!"
        }
        schema = ChangePasswordIn(**data)
        assert schema.old_password == "SenhaAntiga123!"
        assert schema.new_password == "SenhaNova456!"

    def test_passwords_must_match(self):
        data = {
            "old_password": "SenhaAntiga123!",
            "new_password": "SenhaNova456!",
            "new_password2": "SenhaDiferente789!"
        }
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordIn(**data)
        assert "senhas não coincidem" in str(exc_info.value).lower()

    def test_weak_new_password(self):
        data = {
            "old_password": "SenhaAntiga123!",
            "new_password": "123",
            "new_password2": "123"
        }
        with pytest.raises(ValidationError):
            ChangePasswordIn(**data)


class TestPasswordResetRequestIn:
    """Testes do schema de solicitação de reset de senha"""

    def test_valid_request(self):
        data = {"email": "user@teste.com"}
        schema = PasswordResetRequestIn(**data)
        assert schema.email == "user@teste.com"


class TestPasswordResetConfirmIn:
    """Testes do schema de confirmação de reset de senha"""

    def test_valid_confirmation(self):
        data = {
            "uid": "abc123",
            "token": "token_xyz",
            "new_password": "NovaSenha123!",
            "new_password2": "NovaSenha123!"
        }
        schema = PasswordResetConfirmIn(**data)
        assert schema.uid == "abc123"
        assert schema.token == "token_xyz"

    def test_passwords_must_match(self):
        data = {
            "uid": "abc123",
            "token": "token_xyz",
            "new_password": "Senha123!",
            "new_password2": "Senha456!"
        }
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirmIn(**data)
        assert "senhas não coincidem" in str(exc_info.value).lower()


class TestUserOut:
    """Testes do schema de saída do usuário"""

    def test_user_output_serialization(self, member_user):
        data = UserOut.from_orm(member_user)
        
        assert data.id == member_user.id
        assert data.email == member_user.email
        assert data.role == member_user.role
        assert data.photo_url == member_user.photo_url
        assert data.is_trusty == member_user.is_trusty
        assert data.is_active == member_user.is_active
        assert data.date_joined == member_user.date_joined
        assert data.created_at == member_user.created_at
        assert data.role_label == member_user.get_role_display()

    def test_user_out_photo_property(self, member_user):
        data = UserOut.from_orm(member_user)
        assert isinstance(data.photo_url, str)
        assert data.photo_url != ""


class TestMessageOut:
    """Testes do schema de mensagem genérica"""

    def test_message_output(self):
        data = {"detail": "Operação realizada com sucesso"}
        schema = MessageOut(**data)
        assert schema.detail == "Operação realizada com sucesso"