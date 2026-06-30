# tests/tasks/test_init.py
"""
Testes para o módulo __init__.py das tasks.
"""
from ecclesia.apps.users.tasks import (
    send_verification_email,
    send_password_reset_email,
    send_member_invite_email,
)


class TestTaskImports:
    """Testes para verificar importações corretas no __init__."""

    def test_task_imports_available(self):
        """Testa que todas as tasks estão disponíveis via __init__."""
        assert send_verification_email is not None
        assert send_password_reset_email is not None
        assert send_member_invite_email is not None

    def test_task_functions_are_callable(self):
        """Testa que as tasks são callable (podem ser chamadas)."""
        assert callable(send_verification_email)
        assert callable(send_password_reset_email)
        assert callable(send_member_invite_email)

    def test_task_has_shared_task_decorator(self):
        """Testa que as tasks têm o decorador shared_task."""
        # Verifica se as tasks têm atributos do Celery
        assert hasattr(send_verification_email, 'delay')
        assert hasattr(send_verification_email, 'apply_async')
        
        assert hasattr(send_password_reset_email, 'delay')
        assert hasattr(send_password_reset_email, 'apply_async')
        
        assert hasattr(send_member_invite_email, 'delay')
        assert hasattr(send_member_invite_email, 'apply_async')