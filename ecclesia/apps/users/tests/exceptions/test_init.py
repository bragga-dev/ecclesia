import pytest

from ecclesia.apps.users.exceptions import  (
    InvalidCredentials,
    InvalidPassword,
    InvalidToken,
    UserAlreadyExists,
    UserNotFound,
    PermissionDenied,
    EmailNotVerified,
)


class TestExports:
    """Testes para verificar as exportações do módulo"""
    
    def test_all_imports_available(self):
        """Testa se todas as classes estão disponíveis via import do __init__"""
        from ecclesia.apps.users.exceptions import __all__
        
        assert "InvalidCredentials" in __all__
        assert "InvalidPassword" in __all__
        assert "InvalidToken" in __all__
        assert "UserAlreadyExists" in __all__
        assert "UserNotFound" in __all__
        assert "PermissionDenied" in __all__
        assert "EmailNotVerified" in __all__
    
    def test_all_list_completeness(self):
        """Testa se __all__ contém todas as classes esperadas"""
        from ecclesia.apps.users.exceptions import  __all__
        
        expected = [
            "InvalidCredentials",
            "InvalidPassword",
            "InvalidToken",
            "UserAlreadyExists",
            "UserNotFound",
            "PermissionDenied",
            "EmailNotVerified",
        ]
        
        assert set(__all__) == set(expected)
        assert len(__all__) == len(expected)
    
    def test_import_from_package(self):
        """Testa se é possível importar diretamente do pacote"""
        from ecclesia.apps.users import exceptions 
        
        assert hasattr(exceptions, "InvalidCredentials")
        assert hasattr(exceptions, "InvalidPassword")
        assert hasattr(exceptions, "InvalidToken")
        assert hasattr(exceptions, "UserAlreadyExists")
        assert hasattr(exceptions, "UserNotFound")
        assert hasattr(exceptions, "PermissionDenied")
        assert hasattr(exceptions, "EmailNotVerified")
    
    def test_classes_are_same(self):
        """Testa se as classes importadas são as mesmas"""
        from ecclesia.apps.users.exceptions.auth import InvalidCredentials as AuthInvalidCredentials
        from ecclesia.apps.users.exceptions.user import UserAlreadyExists as UserUserAlreadyExists
        from ecclesia.apps.users.exceptions.permissions import PermissionDenied as PermissionsPermissionDenied
        
        assert InvalidCredentials is AuthInvalidCredentials
        assert UserAlreadyExists is UserUserAlreadyExists
        assert PermissionDenied is PermissionsPermissionDenied