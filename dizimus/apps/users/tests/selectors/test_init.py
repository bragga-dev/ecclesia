"""
Testes para o arquivo __init__ dos selectors.
Verifica se todas as funções estão sendo exportadas corretamente.
"""
import importlib

from django.test import TestCase

from dizimus.apps.users.selectors import __all__ as selector_exports


class TestSelectorsInit(TestCase):
    """Testes para verificar as exportações do módulo selectors."""

    def test_init_exports_all_user_selectors(self):
        """Verifica se todos os selectors de user estão em __all__."""
        user_selectors = [
            "get_user_by_id",
            "get_user_by_email", 
            "get_user_by_slug",
            "email_exists",
            "username_exists",
            "get_active_users",
            "get_users_by_role",
        ]
        
        for selector in user_selectors:
            self.assertIn(selector, selector_exports)

    def test_init_exports_all_profile_selectors(self):
        """Verifica se todos os selectors de profile estão em __all__."""
        profile_selectors = [
            "get_church_by_cnpj",
            "get_member_by_cpf",
            "get_church_by_user_id",
            "get_member_by_user_id",
        ]
        
        for selector in profile_selectors:
            self.assertIn(selector, selector_exports)

    def test_all_contains_only_valid_export_names(self):
        """Verifica se todos os nomes em __all__ são strings e são válidos."""
        for export_name in selector_exports:
            self.assertIsInstance(export_name, str)
            self.assertTrue(export_name.isidentifier())

    def test_selectors_module_has_correct_docstring(self):
        """Verifica se o módulo tem a docstring correta."""
        import dizimus.apps.users.selectors as selectors_module
        
        docstring = selectors_module.__doc__
        self.assertIsNotNone(docstring)
        self.assertIn("Selectors", docstring)