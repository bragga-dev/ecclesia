# test_user_selectors.py
"""
Testes para os selectors de User.
"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest
from django.test import TestCase
from django.utils import timezone

from dizimus.apps.users.models import User, ROLE_ADMIN, ROLE_MEMBER, ROLE_CHURCH
from dizimus.apps.users.selectors.user import (
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


class BaseUserSelectorTest(TestCase):
    """Classe base com dados de teste para User selectors."""

    @classmethod
    def setUpTestData(cls):
        """Configura dados de teste uma vez para toda a classe."""
        # Usuário ativo membro
        cls.member_user = User.objects.create_user(
            email="john@example.com",
            password="testpass123",
            role=ROLE_MEMBER,
            is_active=True,
            is_trusty=True,
            is_staff=False,
        )

        # Usuário ativo igreja
        cls.church_user = User.objects.create_user(
            email="church@example.com",
            password="testpass123",
            role=ROLE_CHURCH,
            is_active=True,
            is_trusty=False,
            is_staff=True,
        )

        # Usuário inativo membro
        cls.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="testpass123",
            role=ROLE_MEMBER,
            is_active=False,
            is_trusty=False,
            is_staff=False,
        )

        # Usuário admin - DEVE usar create_superuser
        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )


class TestUserSelectors(BaseUserSelectorTest):
    """Testes para os selectors de User."""

    # ── Busca individual ──────────────────────────────────────────────────────

    def test_get_user_by_id_success(self):
        """Deve retornar o usuário quando ID existe."""
        result = get_user_by_id(self.member_user.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.member_user.id)
        self.assertEqual(result.email, "john@example.com")

    def test_get_user_by_id_not_found(self):
        """Deve retornar None quando ID não existe."""
        non_existent_id = uuid.uuid4()
        result = get_user_by_id(non_existent_id)

        self.assertIsNone(result)

    def test_get_user_by_email_success(self):
        """Deve retornar o usuário quando email existe (case insensitive)."""
        result = get_user_by_email("JOHN@EXAMPLE.COM")

        self.assertIsNotNone(result)
        self.assertEqual(result.email, "john@example.com")

    def test_get_user_by_email_not_found(self):
        """Deve retornar None quando email não existe."""
        result = get_user_by_email("nonexistent@example.com")

        self.assertIsNone(result)

    def test_get_user_by_email_empty_string(self):
        """Deve retornar None para email vazio."""
        result = get_user_by_email("")

        self.assertIsNone(result)



    @pytest.mark.skip(reason="User model does not have a slug field")
    def test_get_user_by_slug_not_found(self):
        pass

    # ── Verificações de existência ──────────────────────────────────────────

    def test_email_exists_true(self):
        """Deve retornar True quando email existe."""
        result = email_exists("john@example.com")
        self.assertTrue(result)

    def test_email_exists_false(self):
        """Deve retornar False quando email não existe."""
        result = email_exists("nonexistent@example.com")
        self.assertFalse(result)

    def test_email_exists_case_insensitive(self):
        """Deve ser case insensitive na verificação de email."""
        result = email_exists("JOHN@EXAMPLE.COM")
        self.assertTrue(result)

    def test_email_exists_with_exclude_id(self):
        """Deve excluir um ID específico na verificação."""
        # Sem exclusão - existe
        self.assertTrue(email_exists("john@example.com"))

        # Com exclusão do próprio usuário - não existe (não há outro com mesmo email)
        self.assertFalse(email_exists("john@example.com", exclude_id=self.member_user.id))

        # Email único não existe
        unique_email = "unique_test_123@example.com"
        self.assertFalse(email_exists(unique_email))
        self.assertFalse(email_exists(unique_email, exclude_id=self.member_user.id))

    def test_user_exists_true(self):
        """Deve retornar True quando usuário existe."""
        result = user_exists(self.member_user.id)
        self.assertTrue(result)

    def test_user_exists_false(self):
        """Deve retornar False quando usuário não existe."""
        result = user_exists(uuid.uuid4())
        self.assertFalse(result)

    # ── Listagens ────────────────────────────────────────────────────────────

    def test_get_all_users(self):
        """Deve retornar todos os usuários."""
        result = get_all_users()
        self.assertEqual(result.count(), 4)
        self.assertIn(self.member_user, result)
        self.assertIn(self.church_user, result)
        self.assertIn(self.inactive_user, result)
        self.assertIn(self.admin_user, result)

    def test_get_active_users(self):
        """Deve retornar apenas usuários ativos."""
        result = get_active_users()
        self.assertEqual(result.count(), 3)
        self.assertIn(self.member_user, result)
        self.assertIn(self.church_user, result)
        self.assertIn(self.admin_user, result)
        self.assertNotIn(self.inactive_user, result)

    def test_get_inactive_users(self):
        """Deve retornar usuários inativos."""
        result = get_inactive_users()
        self.assertEqual(result.count(), 1)
        self.assertIn(self.inactive_user, result)

    def test_get_users_by_role_member(self):
        """Deve retornar usuários com role member."""
        result = get_users_by_role(ROLE_MEMBER)
        self.assertEqual(result.count(), 2)
        for user in result:
            self.assertEqual(user.role, ROLE_MEMBER)

    def test_get_users_by_role_church(self):
        """Deve retornar usuários com role church."""
        result = get_users_by_role(ROLE_CHURCH)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "church@example.com")

    def test_get_users_by_role_admin(self):
        """Deve retornar usuários com role admin."""
        result = get_users_by_role(ROLE_ADMIN)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "admin@example.com")

    def test_get_users_by_role_empty(self):
        """Deve retornar queryset vazio quando role não existe."""
        result = get_users_by_role("invalid_role")
        self.assertEqual(result.count(), 0)

    def test_get_trusty_users(self):
        """Deve retornar apenas usuários confiáveis."""
        result = get_trusty_users()
        self.assertEqual(result.count(), 2)
        self.assertIn(self.member_user, result)
        self.assertIn(self.admin_user, result)
        self.assertNotIn(self.church_user, result)
        self.assertNotIn(self.inactive_user, result)

    def test_get_staff_users(self):
        """Deve retornar usuários com acesso admin."""
        result = get_staff_users()
        self.assertEqual(result.count(), 2)
        self.assertIn(self.church_user, result)
        self.assertIn(self.admin_user, result)
        self.assertNotIn(self.member_user, result)

    # ── Exclusões ────────────────────────────────────────────────────────────

    def test_get_users_excluding_id(self):
        """Deve retornar todos os usuários exceto o informado."""
        result = get_users_excluding_id(self.member_user.id)
        self.assertEqual(result.count(), 3)
        self.assertNotIn(self.member_user, result)
        self.assertIn(self.church_user, result)
        self.assertIn(self.inactive_user, result)
        self.assertIn(self.admin_user, result)

    def test_get_users_excluding_role(self):
        """Deve retornar usuários que não possuem o role informado."""
        result = get_users_excluding_role(ROLE_MEMBER)
        self.assertEqual(result.count(), 2)
        self.assertIn(self.church_user, result)
        self.assertIn(self.admin_user, result)
        self.assertNotIn(self.member_user, result)
        self.assertNotIn(self.inactive_user, result)

    # ── Ordenação ────────────────────────────────────────────────────────────

    def test_get_users_ordered_by_date_descending(self):
        """Deve retornar usuários ordenados por data decrescente."""
        result = get_users_ordered_by_date(descending=True)
        self.assertEqual(result.count(), 4)
        # O admin foi criado por último, deve ser o primeiro
        self.assertEqual(result.first().id, self.admin_user.id)

    def test_get_users_ordered_by_date_ascending(self):
        """Deve retornar usuários ordenados por data crescente."""
        result = get_users_ordered_by_date(descending=False)
        self.assertEqual(result.count(), 4)
        # O member foi criado primeiro, deve ser o primeiro
        self.assertEqual(result.first().id, self.member_user.id)

    # ── Combinados ───────────────────────────────────────────────────────────

    def test_get_active_users_by_role(self):
        """Deve retornar usuários ativos de um role específico."""
        result = get_active_users_by_role(ROLE_MEMBER)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "john@example.com")

    def test_get_active_users_by_role_inactive(self):
        """Não deve retornar usuários inativos."""
        result = get_active_users_by_role(ROLE_MEMBER)
        self.assertNotIn(self.inactive_user, result)

    # ── Search ───────────────────────────────────────────────────────────────

    def test_search_users_by_email(self):
        """Deve buscar usuários por email."""
        result = search_users("john@example")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "john@example.com")

    def test_search_users_empty_query(self):
        """Deve retornar queryset vazio para query vazia."""
        result = search_users("")
        self.assertEqual(result.count(), 0)

        result = search_users("   ")
        self.assertEqual(result.count(), 0)

    def test_search_users_by_role_and_status(self):
        """Deve filtrar usuários por role e status."""
        result = search_users_by_role_and_status(ROLE_MEMBER, True)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "john@example.com")

        result = search_users_by_role_and_status(ROLE_MEMBER, False)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "inactive@example.com")

        result = search_users_by_role_and_status(ROLE_CHURCH, True)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().email, "church@example.com")

    def test_get_users_by_date_range(self):
        """Deve buscar usuários em um período de datas."""
        now = timezone.now()
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)

        result = get_users_by_date_range(start, end)
        self.assertEqual(result.count(), 4)

        # Período antigo (antes dos usuários)
        old_start = now - timedelta(days=10)
        old_end = now - timedelta(days=8)
        result = get_users_by_date_range(old_start, old_end)
        self.assertEqual(result.count(), 0)

    # ── Select Related ──────────────────────────────────────────────────────

    def test_get_user_with_related_success(self):
        """Deve retornar usuário com select_related."""
        result = get_user_with_related(self.member_user.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.member_user.id)


class TestUserSelectorsWithChurchAndMember(TestCase):
    """Testes para select_related com Church e Member."""

    def setUp(self):
        """Configura dados com Church e Member."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            role=ROLE_MEMBER,
            is_active=True,
        )

        # Cria Member relacionado ao User
        from dizimus.apps.users.models import Member
        self.member = Member.objects.create(
            user=self.user,
            cpf="567.364.460-40",
            first_name="Test",
            last_name="User",
        )

    def test_get_user_with_related_has_member(self):
        """Deve carregar o member relacionado."""
        result = get_user_with_related(self.user.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.member.cpf, "567.364.460-40")