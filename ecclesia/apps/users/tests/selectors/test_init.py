# test_init.py
"""
Testes para o arquivo __init__ dos selectors.
Verifica se todas as funções estão sendo exportadas corretamente.
"""
from django.test import TestCase

from ecclesia.apps.users.selectors import __all__ as selector_exports


class TestSelectorsInit(TestCase):
    """Testes para verificar as exportações do módulo selectors."""

    def test_init_exports_all_user_selectors(self):
        """Verifica se todos os selectors de user estão em __all__."""
        user_selectors = [
            "get_user_by_id",
            "get_user_by_email",
            "get_user_by_slug",
            "email_exists",
            "user_exists",
            "get_all_users",
            "get_active_users",
            "get_inactive_users",
            "get_users_by_role",
            "get_trusty_users",
            "get_staff_users",
            "get_users_excluding_id",
            "get_users_excluding_role",
            "get_users_ordered_by_date",
            "get_active_users_by_role",
            "get_user_with_related",
            "search_users",
            "search_users_by_role_and_status",
            "get_users_by_date_range",
        ]

        for selector in user_selectors:
            self.assertIn(selector, selector_exports)

    def test_init_exports_all_member_selectors(self):
        """Verifica se todos os selectors de member estão em __all__."""
        member_selectors = [
            "get_member_by_id",
            "get_member_by_user_id",
            "get_member_by_slug",
            "get_member_by_username",
            "get_member_by_cpf",
            "member_exists",
            "username_exists",
            "cpf_exists",
            "get_all_members",
            "get_members_excluding_id",
            "get_members_ordered_by_name",
            "get_member_with_user",
            "get_member_with_addresses",
            "get_member_full",
            "get_member_church",
            "get_addresses_by_member",
            "get_member_principal_address",
            "get_member_address_by_id",
            "get_address_by_id_and_member",
            "search_members",
            "search_members_by_username",
            "search_members_by_city",
            "get_members_by_birth_month",
        ]

        for selector in member_selectors:
            self.assertIn(selector, selector_exports)

    def test_init_exports_all_church_selectors(self):
        """Verifica se todos os selectors de church estão em __all__."""
        church_selectors = [
            "get_church_by_id",
            "get_church_by_user_id",
            "get_church_by_slug",
            "get_church_by_cnpj",
            "church_exists",
            "cnpj_exists",
            "get_all_churches",
            "get_verified_churches",
            "get_unverified_churches",
            "get_churches_by_type",
            "get_churches_by_parent",
            "get_headquarters",
            "get_churches_excluding_id",
            "get_churches_ordered_by_name",
            "get_church_with_user",
            "get_church_with_addresses",
            "get_church_with_children",
            "get_church_full",
            "get_addresses_by_church",
            "get_church_principal_address",
            "get_church_address_by_id",
            "get_address_by_id_and_church",
            "search_churches",
            "search_verified_churches",
        ]

        for selector in church_selectors:
            self.assertIn(selector, selector_exports)

    def test_all_contains_only_valid_export_names(self):
        """Verifica se todos os nomes em __all__ são strings e são válidos."""
        for export_name in selector_exports:
            self.assertIsInstance(export_name, str)
            self.assertTrue(export_name.isidentifier())

    def test_selectors_module_has_correct_docstring(self):
        """Verifica se o módulo tem a docstring correta."""
        import ecclesia.apps.users.selectors as selectors_module

        docstring = selectors_module.__doc__
        self.assertIsNotNone(docstring)
        self.assertIn("Selectors", docstring)