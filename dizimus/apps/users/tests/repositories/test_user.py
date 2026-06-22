# dizimus/apps/users/tests/repositories/test_user.py

import pytest
from django.core.exceptions import ValidationError
from dizimus.apps.users.repositories.user import create_user, activate_user, deactivate_user
from dizimus.apps.users.models import User


@pytest.mark.django_db
class TestUserRepository:

    def test_create_user_success(self, db):
        user = create_user(
            email="joao@teste.com",
            password="SenhaForte123!",
            role="member"
        )

        assert user.id is not None
        assert user.email == "joao@teste.com"
        assert user.role == "member"
        assert user.is_active is False
        assert user.is_trusty is False

    def test_create_church_user(self, db):
        user = create_user(
            email="igreja@teste.com",
            password="SenhaForte123!",
            role="church"
        )

        assert user.role == "church"
        assert user.is_active is False
        assert user.is_trusty is False

    def test_create_member_user(self, db):
        user = create_user(
            email="membro@teste.com",
            password="SenhaForte123!",
            role="member"
        )

        assert user.role == "member"
        assert user.is_active is False
        assert user.is_trusty is False

    def test_create_user_with_invalid_role(self, db):
        """Deve lançar erro ao criar com role inválida"""
        with pytest.raises(ValidationError):
            create_user(
                email="invalido@teste.com",
                password="SenhaForte123!",
                role="invalid_role"
            )

    def test_create_user_duplicate_email(self, db):
        """Deve lançar erro ao criar com email duplicado"""
        create_user(
            email="duplicado@teste.com",
            password="SenhaForte123!",
            role="member"
        )

        with pytest.raises(Exception):  # IntegrityError
            create_user(
                email="duplicado@teste.com",
                password="OutraSenha123!",
                role="member"
            )

    def test_activate_user(self, member_user):
        """Deve ativar usuário"""
        assert member_user.is_active is False
        assert member_user.is_trusty is False

        activated_user = activate_user(member_user)

        assert activated_user.is_active is True
        assert activated_user.is_trusty is True

    def test_activate_already_active_user(self, db):
        """Ativar usuário já ativo não deve causar erro"""
        user = create_user(
            email="ativo@teste.com",
            password="SenhaForte123!",
            role="member"
        )

        activate_user(user)
        activate_user(user)  # segunda vez

        assert user.is_active is True
        assert user.is_trusty is True

    def test_deactivate_user(self, member_user):
        """Deve desativar usuário"""
        # Primeiro ativa
        activate_user(member_user)
        assert member_user.is_active is True
        assert member_user.is_trusty is True

        # Depois desativa
        deactivated_user = deactivate_user(member_user)

        assert deactivated_user.is_active is False
        assert deactivated_user.is_trusty is False

    def test_deactivate_already_inactive_user(self, db):
        """Desativar usuário já inativo não deve causar erro"""
        user = create_user(
            email="inativo@teste.com",
            password="SenhaForte123!",
            role="member"
        )

        assert user.is_active is False
        assert user.is_trusty is False

        deactivate_user(user)  # não deve lançar erro

        assert user.is_active is False
        assert user.is_trusty is False

    def test_activate_user_does_not_change_other_fields(self, member_user):
        """Ativar usuário não deve alterar outros campos"""
        original_email = member_user.email
        original_role = member_user.role

        activate_user(member_user)

        assert member_user.email == original_email
        assert member_user.role == original_role