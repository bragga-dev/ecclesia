# test_church_selectors.py
"""
Testes para os selectors de Church.
"""
import uuid

from django.test import TestCase

from dizimus.apps.users.models import User, Church, ChurchAddress, ROLE_CHURCH, ROLE_MEMBER
from dizimus.apps.users.selectors.church_selector import (
    get_church_by_id,
    get_church_by_user_id,
    get_church_by_slug,
    get_church_by_cnpj,
    church_exists,
    cnpj_exists,
    get_all_churches,
    get_verified_churches,
    get_unverified_churches,
    get_churches_by_type,
    get_churches_by_parent,
    get_headquarters,
    get_churches_excluding_id,
    get_churches_ordered_by_name,
    get_church_with_user,
    get_church_with_addresses,
    get_church_with_children,
    get_church_full,
    get_addresses_by_church,
    get_church_principal_address,
    get_church_address_by_id,
    get_address_by_id_and_church,
    search_churches,
    search_verified_churches,
)


class BaseChurchSelectorTest(TestCase):
    """Classe base com dados de teste para Church selectors."""

    @classmethod
    def setUpTestData(cls):
        """Configura dados de teste uma vez para toda a classe."""
        cls.user = User.objects.create_user(
            email="church@example.com",
            password="testpass123",
            role=ROLE_CHURCH,
            is_active=True,
        )

        cls.church = Church.objects.create(
            user=cls.user,
            cnpj="16.196.634/0001-00",
            full_name="Igreja Central",
            church_type=Church.ChurchType.HEADQUARTERS,
            is_verified=True,
        )

        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            role=ROLE_CHURCH,
            is_active=True,
        )

        cls.other_church = Church.objects.create(
            user=cls.other_user,
            cnpj="63.356.655/0001-17",
            full_name="Igreja Comunidade",
            church_type=Church.ChurchType.COMMUNITY,
            parent_church=cls.church,
            is_verified=False,
        )

        # Endereços
        cls.address = ChurchAddress.objects.create(
            church=cls.church,
            road="Av. Principal",
            number="1000",
            district="Centro",
            city="São Paulo",
            state="SP",
            cep="01000-000",
            principal=True,
        )

        cls.secondary_address = ChurchAddress.objects.create(
            church=cls.church,
            road="Rua Secundária",
            number="200",
            district="Vila Nova",
            city="São Paulo",
            state="SP",
            cep="02000-000",
            principal=False,
        )


class TestChurchSelectors(BaseChurchSelectorTest):
    """Testes para os selectors de Church."""

    # ── Busca individual ──────────────────────────────────────────────────────

    def test_get_church_by_id_success(self):
        """Deve retornar a igreja quando ID existe."""
        result = get_church_by_id(self.church.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.church.id)
        self.assertEqual(result.full_name, "Igreja Central")

    def test_get_church_by_id_not_found(self):
        """Deve retornar None quando ID não existe."""
        result = get_church_by_id(uuid.uuid4())
        self.assertIsNone(result)

    def test_get_church_by_user_id_success(self):
        """Deve retornar a igreja quando user_id existe."""
        result = get_church_by_user_id(self.user.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, self.user.id)

    def test_get_church_by_user_id_not_found(self):
        """Deve retornar None quando user_id não tem igreja."""
        user_without_church = User.objects.create_user(
            email="no_church@example.com",
            password="testpass123",
            role=ROLE_MEMBER,
            is_active=True,
        )

        result = get_church_by_user_id(user_without_church.id)
        self.assertIsNone(result)

    def test_get_church_by_slug_success(self):
        """Deve retornar a igreja quando slug existe."""
        result = get_church_by_slug(self.church.slug)

        self.assertIsNotNone(result)
        self.assertEqual(result.slug, self.church.slug)

    def test_get_church_by_slug_not_found(self):
        """Deve retornar None quando slug não existe."""
        result = get_church_by_slug("slug-inexistente")
        self.assertIsNone(result)

    def test_get_church_by_cnpj_success(self):
        """Deve retornar a igreja quando CNPJ existe."""
        result = get_church_by_cnpj("16.196.634/0001-00")

        self.assertIsNotNone(result)
        self.assertEqual(result.cnpj, "16.196.634/0001-00")

    def test_get_church_by_cnpj_not_found(self):
        """Deve retornar None quando CNPJ não existe."""
        result = get_church_by_cnpj("00.000.000/0000-00")
        self.assertIsNone(result)

    def test_get_church_by_cnpj_empty_string(self):
        """Deve retornar None para CNPJ vazio."""
        result = get_church_by_cnpj("")
        self.assertIsNone(result)

    # ── Verificações de existência ──────────────────────────────────────────

    def test_church_exists_true(self):
        """Deve retornar True quando igreja existe."""
        result = church_exists(self.church.id)
        self.assertTrue(result)

    def test_church_exists_false(self):
        """Deve retornar False quando igreja não existe."""
        result = church_exists(uuid.uuid4())
        self.assertFalse(result)

    def test_cnpj_exists_true(self):
        """Deve retornar True quando CNPJ existe."""
        result = cnpj_exists("16.196.634/0001-00")
        self.assertTrue(result)

    def test_cnpj_exists_false(self):
        """Deve retornar False quando CNPJ não existe."""
        result = cnpj_exists("00.000.000/0000-00")
        self.assertFalse(result)

    def test_cnpj_exists_with_exclude_id(self):
        """Deve excluir um ID específico na verificação de CNPJ."""
        self.assertTrue(cnpj_exists("16.196.634/0001-00"))
        self.assertFalse(cnpj_exists("16.196.634/0001-00", exclude_id=self.church.id))

    # ── Listagens ────────────────────────────────────────────────────────────

    def test_get_all_churches(self):
        """Deve retornar todas as igrejas."""
        result = get_all_churches()
        self.assertEqual(result.count(), 2)
        self.assertIn(self.church, result)
        self.assertIn(self.other_church, result)

    def test_get_verified_churches(self):
        """Deve retornar apenas igrejas verificadas."""
        result = get_verified_churches()
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_get_unverified_churches(self):
        """Deve retornar igrejas não verificadas."""
        result = get_unverified_churches()
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.other_church.id)

    def test_get_churches_by_type_headquarters(self):
        """Deve retornar igrejas por tipo (sede)."""
        result = get_churches_by_type(Church.ChurchType.HEADQUARTERS)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_get_churches_by_type_community(self):
        """Deve retornar igrejas por tipo (comunidade)."""
        result = get_churches_by_type(Church.ChurchType.COMMUNITY)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.other_church.id)

    def test_get_churches_by_type_empty(self):
        """Deve retornar queryset vazio para tipo inexistente."""
        result = get_churches_by_type("invalid_type")
        self.assertEqual(result.count(), 0)

    def test_get_churches_by_parent(self):
        """Deve retornar igrejas filhas de uma sede."""
        result = get_churches_by_parent(self.church.id)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.other_church.id)

    def test_get_headquarters(self):
        """Deve retornar apenas sedes/matrizes."""
        result = get_headquarters()
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_get_churches_excluding_id(self):
        """Deve retornar todas as igrejas exceto a informada."""
        result = get_churches_excluding_id(self.church.id)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.other_church.id)

    def test_get_churches_ordered_by_name(self):
        """Deve retornar igrejas ordenadas por nome."""
        result = get_churches_ordered_by_name()
        self.assertEqual(result.count(), 2)
        self.assertEqual(result.first().full_name, "Igreja Central")
        self.assertEqual(result.last().full_name, "Igreja Comunidade")

    # ── Com select_related / prefetch ──────────────────────────────────────

    def test_get_church_with_user(self):
        """Deve retornar igreja com select_related no User."""
        result = get_church_with_user(self.church.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.user.email, "church@example.com")

    def test_get_church_with_addresses(self):
        """Deve retornar igreja com prefetch_related nos endereços."""
        result = get_church_with_addresses(self.church.id)

        self.assertIsNotNone(result)
        addresses = list(result.addresses.all())
        self.assertEqual(len(addresses), 2)

    def test_get_church_with_children(self):
        """Deve retornar sede com prefetch das igrejas filhas."""
        result = get_church_with_children(self.church.id)

        self.assertIsNotNone(result)
        children = list(result.child_churches.all())
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].id, self.other_church.id)

    def test_get_church_full(self):
        """Deve retornar igreja com user, addresses e child_churches."""
        result = get_church_full(self.church.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.user.email, "church@example.com")
        self.assertEqual(result.addresses.count(), 2)
        self.assertEqual(result.child_churches.count(), 1)

    # ── ChurchAddress ────────────────────────────────────────────────────────

    def test_get_addresses_by_church(self):
        """Deve retornar todos os endereços de uma igreja."""
        result = get_addresses_by_church(self.church.id)
        self.assertEqual(result.count(), 2)
        self.assertIn(self.address, result)
        self.assertIn(self.secondary_address, result)

    def test_get_church_principal_address(self):
        """Deve retornar o endereço principal da igreja."""
        result = get_church_principal_address(self.church.id)

        self.assertIsNotNone(result)
        self.assertTrue(result.principal)
        self.assertEqual(result.road, "Av. Principal")

    def test_get_church_principal_address_not_found(self):
        """Deve retornar None quando não há endereço principal."""
        result = get_church_principal_address(self.other_church.id)
        self.assertIsNone(result)

    def test_get_church_address_by_id_success(self):
        """Deve retornar endereço por ID."""
        result = get_church_address_by_id(self.address.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.address.id)

    def test_get_church_address_by_id_not_found(self):
        """Deve retornar None quando endereço não existe."""
        result = get_church_address_by_id(uuid.uuid4())
        self.assertIsNone(result)

    def test_get_address_by_id_and_church_success(self):
        """Deve retornar endereço por ID e igreja."""
        result = get_address_by_id_and_church(self.address.id, self.church.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.address.id)
        self.assertEqual(result.church_id, self.church.id)

    def test_get_address_by_id_and_church_wrong_church(self):
        """Deve retornar None quando endereço não pertence à igreja."""
        result = get_address_by_id_and_church(self.address.id, self.other_church.id)
        self.assertIsNone(result)

    # ── Search ───────────────────────────────────────────────────────────────

    def test_search_churches_by_name(self):
        """Deve buscar igrejas por nome."""
        result = search_churches("Central")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_search_churches_by_cnpj(self):
        """Deve buscar igrejas por CNPJ."""
        result = search_churches("16.196.634")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_search_churches_by_city(self):
        """Deve buscar igrejas por cidade."""
        result = search_churches("São Paulo")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_search_churches_empty_query(self):
        """Deve retornar queryset vazio para query vazia."""
        result = search_churches("")
        self.assertEqual(result.count(), 0)

        result = search_churches("   ")
        self.assertEqual(result.count(), 0)

    def test_search_verified_churches(self):
        """Deve buscar apenas igrejas verificadas."""
        result = search_verified_churches("Igreja")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

        result = search_verified_churches("São Paulo")
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, self.church.id)

    def test_search_verified_churches_empty_query(self):
        """Deve retornar queryset vazio para query vazia."""
        result = search_verified_churches("")
        self.assertEqual(result.count(), 0)

        result = search_verified_churches("   ")
        self.assertEqual(result.count(), 0)