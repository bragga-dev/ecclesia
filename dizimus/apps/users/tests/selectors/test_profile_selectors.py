"""
Testes para os selectors de Profile (Church e Member).
"""
import uuid

from django.test import TestCase

from dizimus.apps.users.models import Church, Member, User
from dizimus.apps.users.selectors.profile import (
    get_church_by_cnpj,
    get_member_by_cpf,
    get_church_by_user_id,
    get_member_by_user_id,
)


class TestChurchSelectors(TestCase):
    """Testes para selectors de Church."""

    def setUp(self):
        """Configura dados de teste para Church."""
        self.church_user = User.objects.create_user(
            username="church_user",
            email="church@example.com",
            password="testpass123",
            first_name="Church",
            last_name="Admin",
            role="church"
        )
        
        # Criar Church com os campos corretos do modelo
        self.church = Church.objects.create(
            user=self.church_user,
            cnpj="12.345.678/0001-90",
            # Outros campos serão definidos conforme o modelo real
            # Por enquanto, apenas o essencial
        )
        
        # Se o modelo Church tiver outros campos obrigatórios, adicione-os aqui
        # Exemplo: self.church.church_name = "Igreja Teste" (se existir)
        
        self.other_church_user = User.objects.create_user(
            username="other_church",
            email="other@example.com",
            password="testpass123",
            first_name="Other",
            last_name="Church",
            role="church"
        )
        
        self.other_church = Church.objects.create(
            user=self.other_church_user,
            cnpj="98.765.432/0001-10",
        )

    def test_get_church_by_cnpj_success(self):
        """Deve retornar a igreja quando CNPJ existe."""
        result = get_church_by_cnpj("12.345.678/0001-90")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.cnpj, "12.345.678/0001-90")

    def test_get_church_by_cnpj_not_found(self):
        """Deve retornar None quando CNPJ não existe."""
        result = get_church_by_cnpj("00.000.000/0000-00")
        
        self.assertIsNone(result)

    def test_get_church_by_cnpj_none_input(self):
        """Deve retornar None quando CNPJ é None."""
        result = get_church_by_cnpj(None)
        
        self.assertIsNone(result)

    def test_get_church_by_user_id_success(self):
        """Deve retornar a igreja quando user_id existe."""
        result = get_church_by_user_id(self.church_user.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, self.church_user.id)

    def test_get_church_by_user_id_not_found(self):
        """Deve retornar None quando user_id não tem igreja associada."""
        non_church_user = User.objects.create_user(
            username="member_user",
            email="member@example.com",
            password="testpass123",
            first_name="Member",
            last_name="User",
            role="member"
        )
        
        result = get_church_by_user_id(non_church_user.id)
        
        self.assertIsNone(result)

    def test_get_church_by_user_id_invalid_uuid(self):
        """Deve retornar None para UUID inexistente."""
        invalid_uuid = uuid.uuid4()
        result = get_church_by_user_id(invalid_uuid)
        
        self.assertIsNone(result)


class TestMemberSelectors(TestCase):
    """Testes para selectors de Member."""

    def setUp(self):
        """Configura dados de teste para Member."""
        self.member_user = User.objects.create_user(
            username="member_user",
            email="member@example.com",
            password="testpass123",
            first_name="João",
            last_name="Silva",
            role="member"
        )
        
        # Criar Member com os campos corretos do modelo
        self.member = Member.objects.create(
            user=self.member_user,
            cpf="123.456.789-00",
            # Outros campos serão definidos conforme o modelo real
        )
        
        self.other_member_user = User.objects.create_user(
            username="other_member",
            email="other_member@example.com",
            password="testpass123",
            first_name="Maria",
            last_name="Santos",
            role="member"
        )
        
        self.other_member = Member.objects.create(
            user=self.other_member_user,
            cpf="987.654.321-00",
        )

    def test_get_member_by_cpf_success(self):
        """Deve retornar o membro quando CPF existe."""
        result = get_member_by_cpf("123.456.789-00")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.cpf, "123.456.789-00")

    def test_get_member_by_cpf_not_found(self):
        """Deve retornar None quando CPF não existe."""
        result = get_member_by_cpf("000.000.000-00")
        
        self.assertIsNone(result)

    def test_get_member_by_cpf_none_input(self):
        """Deve retornar None quando CPF é None."""
        result = get_member_by_cpf(None)
        
        self.assertIsNone(result)

    def test_get_member_by_user_id_success(self):
        """Deve retornar o membro quando user_id existe."""
        result = get_member_by_user_id(self.member_user.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, self.member_user.id)

    def test_get_member_by_user_id_not_found(self):
        """Deve retornar None quando user_id não tem membro associado."""
        non_member_user = User.objects.create_user(
            username="church_only",
            email="churchonly@example.com",
            password="testpass123",
            first_name="Church",
            last_name="Only",
            role="church"
        )
        
        result = get_member_by_user_id(non_member_user.id)
        
        self.assertIsNone(result)

    def test_get_member_by_user_id_invalid_uuid(self):
        """Deve retornar None para UUID inexistente."""
        invalid_uuid = uuid.uuid4()
        result = get_member_by_user_id(invalid_uuid)
        
        self.assertIsNone(result)


class TestProfileSelectorsEdgeCases(TestCase):
    """Testes para casos extremos dos selectors de Profile."""

    def setUp(self):
        """Configura dados de teste."""
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role="member"
        )

    def test_get_church_by_cnpj_empty_string(self):
        """Deve retornar None quando CNPJ é string vazia."""
        result = get_church_by_cnpj("")
        
        self.assertIsNone(result)

    def test_get_member_by_cpf_empty_string(self):
        """Deve retornar None quando CPF é string vazia."""
        result = get_member_by_cpf("")
        
        self.assertIsNone(result)

    def test_get_church_by_user_id_with_user_has_no_church(self):
        """Deve retornar None quando usuário não tem igreja associada."""
        result = get_church_by_user_id(self.user.id)
        
        self.assertIsNone(result)

    def test_get_member_by_user_id_with_user_has_no_member(self):
        """Deve retornar None quando usuário não tem membro associado."""
        church_user = User.objects.create_user(
            username="church_user2",
            email="church2@example.com",
            password="testpass123",
            first_name="Church",
            last_name="Two",
            role="church"
        )
        
        result = get_member_by_user_id(church_user.id)
        
        self.assertIsNone(result)