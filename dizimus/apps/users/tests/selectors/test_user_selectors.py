"""
Testes para os selectors de User.
"""
import uuid
from unittest.mock import Mock, patch

from django.test import TestCase

from dizimus.apps.users.models import User
from dizimus.apps.users.selectors.user import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_slug,
    email_exists,
    username_exists,
    get_active_users,
    get_users_by_role,
)


class TestUserSelectors(TestCase):
    """Testes para os selectors de User."""

    def setUp(self):
        """Configura dados de teste."""
        self.user1 = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            slug="john-doe",
            role="member",
            is_active=True
        )
        
        self.user2 = User.objects.create_user(
            username="jane_smith",
            email="jane@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
            slug="jane-smith",
            role="church",
            is_active=True
        )
        
        self.user3 = User.objects.create_user(
            username="inactive_user",
            email="inactive@example.com",
            password="testpass123",
            first_name="Inactive",
            last_name="User",
            slug="inactive-user",
            role="member",
            is_active=False
        )

    def test_get_user_by_id_success(self):
        """Deve retornar o usuário quando ID existe."""
        result = get_user_by_id(self.user1.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.user1.id)
        self.assertEqual(result.username, "john_doe")

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
        self.assertEqual(result.username, "john_doe")

    def test_get_user_by_email_not_found(self):
        """Deve retornar None quando email não existe."""
        result = get_user_by_email("nonexistent@example.com")
        
        self.assertIsNone(result)

    def test_get_user_by_slug_success(self):
        """Deve retornar o usuário quando slug existe."""
        result = get_user_by_slug("jane-smith")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.slug, "jane-smith")
        self.assertEqual(result.username, "jane_smith")

    def test_get_user_by_slug_not_found(self):
        """Deve retornar None quando slug não existe."""
        result = get_user_by_slug("nonexistent-slug")
        
        self.assertIsNone(result)

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
        # Não podemos criar outro usuário com o mesmo email (viola unique constraint)
        # Então vamos testar de outra forma: primeiro verificar que o email existe,
        # depois verificar que excluindo o próprio ID retorna False
        
        # Verifica que o email existe
        result_without_exclude = email_exists("john@example.com")
        self.assertTrue(result_without_exclude)
        
        # Verifica que excluindo o próprio usuário, retorna False
        # (pois não há outro usuário com este email)
        result_with_exclude = email_exists("john@example.com", exclude_id=self.user1.id)
        self.assertFalse(result_with_exclude)
        
        # Teste adicional: criar um email único e verificar que não existe
        unique_email = "unique_test_123@example.com"
        result_unique = email_exists(unique_email)
        self.assertFalse(result_unique)
        
        # Verificar que exclude_id não afeta quando não há outros
        result_unique_with_exclude = email_exists(unique_email, exclude_id=self.user1.id)
        self.assertFalse(result_unique_with_exclude)

    def test_username_exists_true(self):
        """Deve retornar True quando username existe."""
        result = username_exists("john_doe")
        
        self.assertTrue(result)

    def test_username_exists_false(self):
        """Deve retornar False quando username não existe."""
        result = username_exists("nonexistent_username")
        
        self.assertFalse(result)

    def test_username_exists_case_insensitive(self):
        """Deve ser case insensitive na verificação de username."""
        result = username_exists("JOHN_DOE")
        
        self.assertTrue(result)

    def test_username_exists_with_exclude_id(self):
        """Deve excluir um ID específico na verificação de username."""
        # Testa username existente sem excluir
        result_without_exclude = username_exists("john_doe")
        self.assertTrue(result_without_exclude)
        
        # Testa excluindo o próprio ID do usuário (deve retornar False
        # pois não há outro usuário com o mesmo username)
        result_with_exclude = username_exists("john_doe", exclude_id=self.user1.id)
        self.assertFalse(result_with_exclude)
        
        # Testa com username que não existe
        unique_username = "nonexistent_user_123"
        result_unique = username_exists(unique_username)
        self.assertFalse(result_unique)
        
        # Exclude_id não deve fazer diferença para username que não existe
        result_unique_with_exclude = username_exists(unique_username, exclude_id=self.user1.id)
        self.assertFalse(result_unique_with_exclude)
        def test_get_active_users(self):
            """Deve retornar apenas usuários ativos."""
            result = get_active_users()
            
            self.assertEqual(len(result), 2)
            self.assertIn(self.user1, result)
            self.assertIn(self.user2, result)
            self.assertNotIn(self.user3, result)

    def test_get_users_by_role_member(self):
        """Deve retornar usuários com role 'member'."""
        result = get_users_by_role("member")
        
        # Temos user1 e user3 como members (user3 é inactive mas ainda é member)
        self.assertEqual(len(result), 2)
        for user in result:
            self.assertEqual(user.role, "member")

    def test_get_users_by_role_church(self):
        """Deve retornar usuários com role 'church'."""
        result = get_users_by_role("church")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, "jane_smith")
        self.assertEqual(result[0].role, "church")

    def test_get_users_by_role_empty(self):
        """Deve retornar lista vazia quando role não existe."""
        result = get_users_by_role("admin")
        
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])


class TestUserSelectorsMocked(TestCase):
    """Testes com mock para validação adicional."""

    @patch('dizimus.apps.users.selectors.user.User.objects')
    def test_get_user_by_id_calls_filter(self, mock_objects):
        """Deve chamar filter com o ID correto."""
        user_id = uuid.uuid4()
        mock_objects.filter.return_value.first.return_value = Mock(spec=User)
        
        get_user_by_id(user_id)
        
        mock_objects.filter.assert_called_once_with(pk=user_id)

    @patch('dizimus.apps.users.selectors.user.User.objects')
    def test_get_user_by_email_calls_filter_iexact(self, mock_objects):
        """Deve chamar filter com email__iexact."""
        email = "test@example.com"
        mock_objects.filter.return_value.first.return_value = Mock(spec=User)
        
        get_user_by_email(email)
        
        mock_objects.filter.assert_called_once_with(email__iexact=email)

    @patch('dizimus.apps.users.selectors.user.User.objects')
    def test_email_exists_without_exclude(self, mock_objects):
        """Deve verificar email sem excluir IDs."""
        mock_objects.filter.return_value.exists.return_value = True
        
        result = email_exists("test@example.com")
        
        mock_objects.filter.assert_called_once_with(email__iexact="test@example.com")
        self.assertTrue(result)

    @patch('dizimus.apps.users.selectors.user.User.objects')
    def test_email_exists_with_exclude(self, mock_objects):
        """Deve excluir ID específico quando fornecido."""
        exclude_id = uuid.uuid4()
        mock_qs = Mock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exclude.return_value.exists.return_value = False
        
        result = email_exists("test@example.com", exclude_id=exclude_id)
        
        mock_objects.filter.assert_called_once_with(email__iexact="test@example.com")
        mock_qs.exclude.assert_called_once_with(pk=exclude_id)
        self.assertFalse(result)