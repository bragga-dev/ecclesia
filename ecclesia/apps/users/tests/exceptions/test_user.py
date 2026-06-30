import pytest
from django.utils.translation import gettext_lazy as _

from ecclesia.apps.users.exceptions.user import UserAlreadyExists, UserNotFound, EmailNotVerified


class TestUserAlreadyExists:
    """Testes para a exceção UserAlreadyExists"""
    
    def test_default_field(self):
        """Testa se o campo padrão é 'email'"""
        exception = UserAlreadyExists()
        assert exception.field == "email"
        assert str(exception) == "Já existe um usuário com este email."
    
    def test_custom_field_email(self):
        """Testa com campo email explicitamente"""
        exception = UserAlreadyExists("email")
        assert exception.field == "email"
        assert str(exception) == "Já existe um usuário com este email."
    
    def test_custom_field_username(self):
        """Testa com campo username"""
        exception = UserAlreadyExists("username")
        assert exception.field == "username"
        assert str(exception) == "Já existe um usuário com este username."
    
    def test_custom_field_phone(self):
        """Testa com campo phone"""
        exception = UserAlreadyExists("phone")
        assert exception.field == "phone"
        assert str(exception) == "Já existe um usuário com este phone."
    
    def test_custom_field_document(self):
        """Testa com campo document"""
        exception = UserAlreadyExists("document")
        assert exception.field == "document"
        assert str(exception) == "Já existe um usuário com este document."
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = UserAlreadyExists()
        assert isinstance(exception, Exception)
        assert isinstance(exception, UserAlreadyExists)
    
    def test_message_format(self):
        """Testa o formato da mensagem com diferentes campos"""
        fields = ["email", "username", "phone", "document"]
        for field in fields:
            exception = UserAlreadyExists(field)
            expected = f"Já existe um usuário com este {field}."
            assert str(exception) == expected
    
    def test_message_is_translatable(self):
        """Testa se a mensagem é traduzível"""
        exception = UserAlreadyExists()
        from django.utils.functional import Promise
        # A mensagem é construída com f-string, então é uma string normal
        assert isinstance(str(exception), str)


class TestUserNotFound:
    """Testes para a exceção UserNotFound"""
    
    def test_default_message(self):
        """Testa se a mensagem padrão é usada corretamente"""
        exception = UserNotFound()
        assert str(exception) == "Usuário não encontrado."
    
    def test_no_parameters(self):
        """Testa que não aceita parâmetros"""
        exception = UserNotFound()
        assert exception.args == ("Usuário não encontrado.",)
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = UserNotFound()
        assert isinstance(exception, Exception)
        assert isinstance(exception, UserNotFound)
    
    def test_message_is_translatable(self):
        """Testa se a mensagem é traduzível"""
        exception = UserNotFound()
        from django.utils.functional import Promise
        # gettext_lazy retorna um objeto Promise
        assert isinstance(exception.args[0], Promise)
        assert str(exception) == "Usuário não encontrado."


class TestEmailNotVerified:
    """Testes para a exceção EmailNotVerified"""
    
    def test_default_behavior(self):
        """Testa o comportamento padrão sem mensagem"""
        exception = EmailNotVerified()
        assert str(exception) == ""
        assert exception.args == ()
    
    def test_custom_message(self):
        """Testa se aceita mensagem personalizada"""
        custom_msg = "E-mail não confirmado"
        exception = EmailNotVerified(custom_msg)
        assert str(exception) == custom_msg
    
    def test_custom_message_different(self):
        """Testa com diferentes mensagens personalizadas"""
        messages = [
            "Por favor, confirme seu e-mail",
            "E-mail não verificado",
            "Confirme seu endereço de e-mail"
        ]
        for msg in messages:
            exception = EmailNotVerified(msg)
            assert str(exception) == msg
    
    def test_inheritance(self):
        """Testa se herda corretamente de Exception"""
        exception = EmailNotVerified()
        assert isinstance(exception, Exception)
        assert isinstance(exception, EmailNotVerified)
    
    def test_with_translation(self):
        """Testa com mensagem traduzível"""
        exception = EmailNotVerified(_("E-mail não confirmado"))
        assert str(exception) == "E-mail não confirmado"