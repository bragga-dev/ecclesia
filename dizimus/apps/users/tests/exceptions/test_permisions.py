import pytest
from django.utils.translation import gettext_lazy as _

from dizimus.apps.users.exceptions.permissions import PermissionDenied


class TestPermissionDenied:
    """Testes para a exceção PermissionDenied"""
    
    def test_default_message(self):
        """Testa se a mensagem padrão é usada corretamente"""
        exception = PermissionDenied()
        assert str(exception) == "Você não tem permissão para realizar esta ação."
    
    def test_custom_message(self):
        """Testa se uma mensagem personalizada é aceita"""
        custom_msg = "Acesso negado"
        exception = PermissionDenied(custom_msg)
        assert str(exception) == custom_msg
    
    def test_custom_message_different(self):
        """Testa com diferentes mensagens personalizadas"""
        messages = [
            "Permissão insuficiente",
            "Ação não autorizada",
            "Você não pode acessar este recurso"
        ]
        for msg in messages:
            exception = PermissionDenied(msg)
            assert str(exception) == msg
    
    def test_message_is_translatable(self):
        """Testa que a mensagem é traduzível"""
        exception = PermissionDenied()
        from django.utils.functional import Promise
        # gettext_lazy retorna um objeto Promise
        assert isinstance(exception.args[0], Promise)
        assert str(exception) == "Você não tem permissão para realizar esta ação."
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = PermissionDenied()
        assert isinstance(exception, Exception)
        assert isinstance(exception, PermissionDenied)
    
    def test_with_translation(self):
        """Testa com mensagem traduzida"""
        exception = PermissionDenied(_("Permissão negada"))
        assert str(exception) == "Permissão negada"
    
    def test_message_type(self):
        """Testa que a mensagem é sempre uma string quando convertida"""
        exception = PermissionDenied()
        assert isinstance(str(exception), str)
        
        exception = PermissionDenied("Teste")
        assert isinstance(str(exception), str)