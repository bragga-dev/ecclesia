"""
Testes do UserManager
─────────────────────
Cobre: _create_user, create_user, create_superuser e normalização de e-mail.
"""

import pytest
from django.core.exceptions import ValidationError

from .conftest import build_user_data


@pytest.mark.django_db
class TestCreateUser:
    """create_user — cria MEMBER ou CHURCH."""

    def test_cria_member_com_dados_minimos(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.pk is not None

    def test_role_padrao_e_member(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.role == User.UserRole.MEMBER

    def test_member_nao_ativo_por_padrao(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.is_active is False

    def test_member_nao_staff_por_padrao(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.is_staff is False

    def test_member_nao_superuser_por_padrao(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.is_superuser is False

    def test_member_nao_trusty_por_padrao(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.is_trusty is False

    def test_cria_church_com_role_church(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data(
            email="church@teste.com",
            username="churchteste",
            role="church",
        ))
        assert user.role == User.UserRole.CHURCH

    def test_church_nao_ativo_por_padrao(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data(
            email="church2@teste.com",
            username="church2",
            role="church",
        ))
        assert user.is_active is False

    def test_cria_user_com_role_admin_levanta_value_error(self):
        from dizimus.apps.users.models.user import User
        with pytest.raises(ValueError, match="create_superuser"):
            User.objects.create_user(**build_user_data(role="admin"))

    def test_email_vazio_levanta_value_error(self):
        from dizimus.apps.users.models.user import User
        with pytest.raises(ValueError, match="e-mail"):
            User.objects.create_user(**build_user_data(email=""))

    def test_senha_e_hasheada(self):
        from dizimus.apps.users.models.user import User
        senha = "SenhaForte123!"
        user = User.objects.create_user(**build_user_data(password=senha))
        assert user.check_password(senha)
        assert user.password != senha

    def test_email_e_normalizado(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data(
            email="Usuario@TESTE.COM",
            username="usernorm",
        ))
        # Django normaliza apenas o domínio para minúsculas
        assert user.email == "Usuario@teste.com"

    def test_date_joined_preenchido_ao_criar(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data())
        assert user.date_joined is not None

    def test_last_login_preenchido_ao_criar(self):
        from dizimus.apps.users.models import User
        user = User.objects.create_user(**build_user_data())
        assert user.last_login is not None


@pytest.mark.django_db
class TestCreateSuperuser:
    """create_superuser — cria ADMIN com todos os flags elevados."""

    def test_cria_superuser_com_dados_minimos(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="su@teste.com",
            username="superusuario",
        ))
        assert user.pk is not None

    def test_superuser_tem_role_admin(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="su2@teste.com", username="su2",
        ))
        assert user.role == User.UserRole.ADMIN

    def test_superuser_e_ativo(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="su3@teste.com", username="su3",
        ))
        assert user.is_active is True

    def test_superuser_e_staff(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="su4@teste.com", username="su4",
        ))
        assert user.is_staff is True

    def test_superuser_e_superuser(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="su5@teste.com", username="su5",
        ))
        assert user.is_superuser is True

    def test_superuser_e_trusty(self):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="su6@teste.com", username="su6",
        ))
        assert user.is_trusty is True

    def test_superuser_com_is_staff_false_levanta_value_error(self):
        from dizimus.apps.users.models.user import User
        with pytest.raises(ValueError, match="is_staff"):
            User.objects.create_superuser(
                **build_user_data(email="su7@teste.com", username="su7"),
                is_staff=False,
            )

    def test_superuser_com_is_superuser_false_levanta_value_error(self):
        from dizimus.apps.users.models.user import User
        with pytest.raises(ValueError, match="is_superuser"):
            User.objects.create_superuser(
                **build_user_data(email="su8@teste.com", username="su8"),
                is_superuser=False,
            )