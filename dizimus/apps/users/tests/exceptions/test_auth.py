import pytest
from django.utils.translation import gettext_lazy as _

from dizimus.apps.users.exceptions.auth import InvalidCredentials, InvalidPassword, InvalidToken


class TestInvalidCredentials:
    """Testes para a exceção InvalidCredentials"""
    
    def test_default_message(self):
        """Testa se a mensagem padrão é usada corretamente"""
        exception = InvalidCredentials()
        assert str(exception) == "E-mail ou senha inválidos."
        assert exception.message == "E-mail ou senha inválidos."
    
    def test_custom_message(self):
        """Testa se uma mensagem personalizada é aceita"""
        custom_msg = "Credenciais incorretas"
        exception = InvalidCredentials(custom_msg)
        assert str(exception) == custom_msg
        assert exception.message == custom_msg
    
    def test_empty_message(self):
        """Testa se None é tratado corretamente"""
        exception = InvalidCredentials(None)
        assert str(exception) == "E-mail ou senha inválidos."
        assert exception.message == "E-mail ou senha inválidos."
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = InvalidCredentials()
        assert isinstance(exception, Exception)
        assert isinstance(exception, InvalidCredentials)
    
    def test_message_is_translatable(self):
        """Testa se a mensagem é traduzível"""
        exception = InvalidCredentials()
        # gettext_lazy retorna um objeto proxy, não uma string direta
        # mas deve ser convertível para string
        assert str(exception) == "E-mail ou senha inválidos."
        # Verifica se a mensagem é do tipo lazy
        from django.utils.functional import Promise
        assert isinstance(exception.message, Promise)
        # Verifica se pode ser convertida para string
        assert isinstance(str(exception.message), str)


class TestInvalidPassword:
    """Testes para a exceção InvalidPassword"""
    
    def test_default_message(self):
        """Testa se a mensagem padrão é usada corretamente"""
        exception = InvalidPassword()
        assert str(exception) == "Senha atual incorreta."
        assert exception.message == "Senha atual incorreta."
    
    def test_custom_message(self):
        """Testa se uma mensagem personalizada é aceita"""
        custom_msg = "Senha atual inválida"
        exception = InvalidPassword(custom_msg)
        assert str(exception) == custom_msg
        assert exception.message == custom_msg
    
    def test_empty_message(self):
        """Testa se None é tratado corretamente"""
        exception = InvalidPassword(None)
        assert str(exception) == "Senha atual incorreta."
        assert exception.message == "Senha atual incorreta."
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = InvalidPassword()
        assert isinstance(exception, Exception)
        assert isinstance(exception, InvalidPassword)
    
    def test_message_is_translatable(self):
        """Testa se a mensagem é traduzível"""
        exception = InvalidPassword()
        from django.utils.functional import Promise
        assert isinstance(exception.message, Promise)
        assert str(exception) == "Senha atual incorreta."


class TestInvalidToken:
    """Testes para a exceção InvalidToken"""
    
    def test_default_message(self):
        """Testa se a mensagem padrão é usada corretamente"""
        exception = InvalidToken()
        assert str(exception) == "Token inválido ou expirado."
        assert exception.message == "Token inválido ou expirado."
    
    def test_custom_message(self):
        """Testa se uma mensagem personalizada é aceita"""
        custom_msg = "Token expirado"
        exception = InvalidToken(custom_msg)
        assert str(exception) == custom_msg
        assert exception.message == custom_msg
    
    def test_empty_message(self):
        """Testa se None é tratado corretamente"""
        exception = InvalidToken(None)
        assert str(exception) == "Token inválido ou expirado."
        assert exception.message == "Token inválido ou expirado."
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = InvalidToken()
        assert isinstance(exception, Exception)
        assert isinstance(exception, InvalidToken)
    
    def test_message_is_translatable(self):
        """Testa se a mensagem é traduzível"""
        exception = InvalidToken()
        from django.utils.functional import Promise
        assert isinstance(exception.message, Promise)
        assert str(exception) == "Token inválido ou expirado."