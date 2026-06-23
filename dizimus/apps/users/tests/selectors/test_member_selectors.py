# test_member_selectors.py
"""
Testes para os selectors de Member.
"""
import uuid
from datetime import date

from django.test import TestCase

from dizimus.apps.users.models import User, Member, MemberAddress, Church, ROLE_MEMBER, ROLE_CHURCH
from dizimus.apps.community.models import MemberChurch
from dizimus.apps.users.selectors.member_selector import (
    get_member_by_id,
    get_member_by_user_id,
    get_member_by_slug,
    get_member_by_username,
    get_member_by_cpf,
    member_exists,
    username_exists,
    cpf_exists,
    get_all_members,
    get_members_excluding_id,
    get_members_ordered_by_name,
    get_member_with_user,
    get_member_with_addresses,
    get_member_full,
    get_member_church,
    get_addresses_by_member,
    get_member_principal_address,
    get_member_address_by_id,
    get_address_by_id_and_member,
    search_members,
    search_members_by_username,
    search_members_by_city,
    get_members_by_birth_month,
)


class BaseMemberSelectorTest(TestCase):
    """Classe base com dados de teste para Member selectors."""

    @classmethod
    def setUpTestData(cls):
        """Configura dados de teste uma vez para toda a classe."""
        cls.user = User.objects.create_user(
            email="member@example.com",
            password="testpass123",
            role=ROLE_MEMBER,
            is_active=True,
        )

        cls.member = Member.objects.create(
            user=cls.user,
            cpf="567.364.460-40",
            first_name="João",
            last_name="Silva",
            username="joao.silva",
            date_of_birth=date(1990, 1, 15),
        )

        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            role=ROLE_MEMBER,
            is_active=True,
        )

        cls.other_member = Member.objects.create(
            user=cls.other_user,
            cpf="161.276.980-22",
            first_name="Maria",
            last_name="Santos",
            username="maria.santos",
            date_of_birth=date(1992, 5, 20),
        )

        # Endereços
        cls.address = MemberAddress.objects.create(
            member=cls.member,
            road="Rua Principal",
            number="123",
            district="Centro",
            city="São Paulo",
            state="SP",
            cep="01000-000",
            principal=True,
        )

        cls.secondary_address = MemberAddress.objects.create(
            member=cls.member,
            road="Rua Secundária",
            number="456",
            district="Vila Nova",
            city="São Paulo",
            state="SP",
            cep="02000-000",
            principal=False,
        )

        # Igreja - USANDO Church.objects.create()
        church_user = User.objects.create_user(
            email="church@example.com",
            password="testpass123",
            role=ROLE_CHURCH,
            is_active=True,
        )

        cls.church = Church.objects.create(
            user=church_user,
            cnpj="16.196.634/0001-00",
            full_name="Igreja Teste",
        )

        cls.member_church = MemberChurch.objects.create(
            member=cls.member,
            church=cls.church,
        )


class TestMemberSelectors(BaseMemberSelectorTest):
    """Testes para os selectors de Member."""

    # ── Busca individual ──────────────────────────────────────────────────────

    def test_get_member_by_id_success(self):
        """Deve retornar o membro quando ID existe."""
        result = get_member_by_id(self.member.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.member.id)
        self.assertEqual(result.username, "joao.silva")

    def test_get_member_by_id_not_found(self):
        """Deve retornar None quando ID não existe."""
        result = get_member_by_id(uuid.uuid4())
        self.assertIsNone(result)

    def test_get_member_by_user_id_success(self):
        """Deve retornar o membro quando user_id existe."""
        result = get_member_by_user_id(self.user.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, self.user.id)

    def test_get_member_by_user_id_not_found(self):
        """Deve retornar None quando user_id não tem membro."""
        user_without_member = User.objects.create_user(
            email="no_member@example.com",
            password="testpass123",
            role=ROLE_CHURCH,
            is_active=True,
        )

        result = get_member_by_user_id(user_without_member.id)
        self.assertIsNone(result)

    def test_get_member_by_slug_success(self):
        """Deve retornar o membro quando slug existe."""
        result = get_member_by_slug(self.member.slug)

        self.assertIsNotNone(result)
        self.assertEqual(result.slug, self.member.slug)

    def test_get_member_by_slug_not_found(self):
        """Deve retornar None quando slug não existe."""
        result = get_member_by_slug("slug-inexistente")
        self.assertIsNone(result)

    def test_get_member_by_username_success(self):
        """Deve retornar o membro quando username existe (case insensitive)."""
        result = get_member_by_username("JOAO.SILVA")

        self.assertIsNotNone(result)
        self.assertEqual(result.username, "joao.silva")

    def test_get_member_by_username_not_found(self):
        """Deve retornar None quando username não existe."""
        result = get_member_by_username("usuario.inexistente")
        self.assertIsNone(result)

    def test_get_member_by_cpf_success(self):
        """Deve retornar o membro quando CPF existe."""
        result = get_member_by_cpf("567.364.460-40")

        self.assertIsNotNone(result)
        self.assertEqual(result.cpf, "567.364.460-40")

    def test_get_member_by_cpf_not_found(self):
        """Deve retornar None quando CPF não existe."""
        result = get_member_by_cpf("000.000.000-00")
        self.assertIsNone(result)

    def test_get_member_by_cpf_empty_string(self):
        """Deve retornar None para CPF vazio."""
        result = get_member_by_cpf("")
        self.assertIsNone(result)

    # ── MemberChurch ─────────────────────────────────────────────────────────

    def test_get_member_church_success(self):
        """Deve retornar o MemberChurch relacionado."""
        result = get_member_church(self.member.id, self.church.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.member_id, self.member.id)
        self.assertEqual(result.church_id, self.church.id)

    def test_get_member_church_not_found(self):
        """Deve lançar DoesNotExist quando não existe."""
        with self.assertRaises(MemberChurch.DoesNotExist):
            get_member_church(uuid.uuid4(), uuid.uuid4())

    # ── Verificações de existência ──────────────────────────────────────────

    def test_member_exists_true(self):
        """Deve retornar True quando membro existe."""
        result = member_exists(self.member.id)
        self.assertTrue(result)

    def test_member_exists_false(self):
        """Deve retornar False quando membro não existe."""
        result = member_exists(uuid.uuid4())
        self.assertFalse(result)

    def test_username_exists_true(self):
        """Deve retornar True quando username existe."""
        result = username_exists("joao.silva")
        self.assertTrue(result)

    def test_username_exists_false(self):
        """Deve retornar False quando username não existe."""
        result = username_exists("usuario.inexistente")
        self.assertFalse(result)

    def test_username_exists_case_insensitive(self):
        """Deve ser case insensitive na verificação de username."""
        result = username_exists("JOAO.SILVA")
        self.assertTrue(result)

    def test_username_exists_with_exclude_id(self):
        """Deve excluir um ID específico na verificação de username."""
        self.assertTrue(username_exists("joao.silva"))
        self.assertFalse(username_exists("joao.silva", exclude_id=self.member.id))
        self.assertFalse(username_exists("usuario.inexistente", exclude_id=self.member.id))

    def test_cpf_exists_true(self):
        """Deve retornar True quando CPF existe."""
        result = cpf_exists("567.364.460-40")
        self.assertTrue(result)

    def test_cpf_exists_false(self):
        """Deve retornar False quando CPF não existe."""
        result = cpf_exists("000.000.000-00")
        self.assertFalse(result)

    def test_cpf_exists_with_exclude_id(self):
        """Deve excluir um ID específico na verificação de CPF."""
        self.assertTrue(cpf_exists("567.364.460-40"))
        self.assertFalse(cpf_exists("567.364.460-40", exclude_id=self.member.id))

    # ── Listagens ────────────────────────────────────────────────────────────

    def test_get_all_members(self):
        """Deve retornar todos os membros."""
        result = get_all_members()
        self.assertEqual(result.count(), 2)
        self.assertIn(self.member, result)
        self.assertIn(self.other_member, result)

    def test_get_members_excluding_id(self):
        """Deve retornar todos os membros exceto o informado."""
        result = get_members_excluding_id(self.member.id)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.other_member.id)

    def test_get_members_ordered_by_name(self):
        """Deve retornar membros ordenados por nome."""
        result = get_members_ordered_by_name()
        self.assertEqual(result.count(), 2)
        self.assertEqual(result.first().username, "joao.silva")
        self.assertEqual(result.last().username, "maria.santos")

    # ── Com select_related / prefetch ──────────────────────────────────────

    def test_get_member_with_user(self):
        """Deve retornar membro com select_related no User."""
        result = get_member_with_user(self.member.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.user.email, "member@example.com")

    def test_get_member_with_addresses(self):
        """Deve retornar membro com prefetch_related nos endereços."""
        result = get_member_with_addresses(self.member.id)

        self.assertIsNotNone(result)
        addresses = list(result.addresses.all())
        self.assertEqual(len(addresses), 2)

    def test_get_member_full(self):
        """Deve retornar membro com user e addresses."""
        result = get_member_full(self.member.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.user.email, "member@example.com")
        self.assertEqual(result.addresses.count(), 2)

    # ── MemberAddress ────────────────────────────────────────────────────────

    def test_get_addresses_by_member(self):
        """Deve retornar todos os endereços de um membro."""
        result = get_addresses_by_member(self.member.id)
        self.assertEqual(result.count(), 2)
        self.assertIn(self.address, result)
        self.assertIn(self.secondary_address, result)

    def test_get_member_principal_address(self):
        """Deve retornar o endereço principal."""
        result = get_member_principal_address(self.member.id)

        self.assertIsNotNone(result)
        self.assertTrue(result.principal)
        self.assertEqual(result.road, "Rua Principal")

    def test_get_member_principal_address_not_found(self):
        """Deve retornar None quando não há endereço principal."""
        result = get_member_principal_address(self.other_member.id)
        self.assertIsNone(result)

    def test_get_member_address_by_id_success(self):
        """Deve retornar endereço por ID."""
        result = get_member_address_by_id(self.address.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.address.id)

    def test_get_member_address_by_id_not_found(self):
        """Deve retornar None quando endereço não existe."""
        result = get_member_address_by_id(uuid.uuid4())
        self.assertIsNone(result)

    def test_get_address_by_id_and_member_success(self):
        """Deve retornar endereço por ID e membro."""
        result = get_address_by_id_and_member(self.address.id, self.member.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.address.id)
        self.assertEqual(result.member_id, self.member.id)

    def test_get_address_by_id_and_member_wrong_member(self):
        """Deve retornar None quando endereço não pertence ao membro."""
        result = get_address_by_id_and_member(self.address.id, self.other_member.id)
        self.assertIsNone(result)

    # ── Search ───────────────────────────────────────────────────────────────

    def test_search_members_by_first_name(self):
        """Deve buscar membros por primeiro nome."""
        result = search_members("João")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "joao.silva")

    def test_search_members_by_last_name(self):
        """Deve buscar membros por último nome."""
        result = search_members("Santos")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "maria.santos")

    def test_search_members_by_cpf(self):
        """Deve buscar membros por CPF."""
        result = search_members("567.364.460")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "joao.silva")

    def test_search_members_by_city(self):
        """Deve buscar membros por cidade do endereço."""
        result = search_members("São Paulo")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "joao.silva")

    def test_search_members_empty_query(self):
        """Deve retornar queryset vazio para query vazia."""
        result = search_members("")
        self.assertEqual(result.count(), 0)

        result = search_members("   ")
        self.assertEqual(result.count(), 0)

    def test_search_members_by_username(self):
        """Deve buscar membros por username."""
        result = search_members_by_username("joao")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "joao.silva")

    def test_search_members_by_username_empty(self):
        """Deve retornar queryset vazio para query vazia."""
        result = search_members_by_username("")
        self.assertEqual(result.count(), 0)

    def test_search_members_by_city(self):
        """Deve buscar membros por cidade."""
        result = search_members_by_city("São Paulo")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "joao.silva")

    def test_search_members_by_city_empty(self):
        """Deve retornar queryset vazio para city vazia."""
        result = search_members_by_city("")
        self.assertEqual(result.count(), 0)

    def test_get_members_by_birth_month(self):
        """Deve buscar membros por mês de aniversário."""
        result = get_members_by_birth_month(1)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "joao.silva")

        result = get_members_by_birth_month(5)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().username, "maria.santos")

        result = get_members_by_birth_month(12)
        self.assertEqual(result.count(), 0)