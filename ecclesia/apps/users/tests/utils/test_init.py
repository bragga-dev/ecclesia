import pytest
from ecclesia.apps.users.utils import EmailService, TokenService
from ecclesia.apps.users.utils import __all__


class TestInit:
    
    def test_imports_are_available(self):
        """Testa que as importações estão disponíveis no módulo."""
        assert EmailService is not None
        assert TokenService is not None
    
    def test_all_contains_correct_classes(self):
        """Testa que __all__ contém as classes esperadas."""
        assert "EmailService" in __all__
        assert "TokenService" in __all__
        assert len(__all__) == 2