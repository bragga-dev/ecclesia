import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from ecclesia.apps.users.utils.email_service import EmailService


class TestEmailService:
    
    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_html_email_success(self, mock_strip_tags, mock_render_to_string, mock_email_class):
        """Testa envio de email HTML com sucesso."""
        # Configurar mocks
        mock_render_to_string.return_value = "<html>Test content</html>"
        mock_strip_tags.return_value = "Test content"
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        # Dados de teste
        subject = "Test Subject"
        to_email = "test@example.com"
        template_name = "test_template.html"
        context = {"user": "Test User"}
        
        # Executar
        EmailService.send_html_email(subject, to_email, template_name, context)
        
        # Verificações
        mock_render_to_string.assert_called_once_with(template_name, context)
        mock_strip_tags.assert_called_once_with("<html>Test content</html>")
        mock_email_class.assert_called_once_with(
            subject=subject,
            body="Test content",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        mock_email_instance.attach_alternative.assert_called_once_with("<html>Test content</html>", "text/html")
        mock_email_instance.send.assert_called_once_with(fail_silently=False)
    
    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_html_email_with_custom_from_email(self, mock_strip_tags, mock_render_to_string, mock_email_class):
        """Testa envio de email com from_email customizado."""
        mock_render_to_string.return_value = "<html>Test content</html>"
        mock_strip_tags.return_value = "Test content"
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        custom_from = "custom@example.com"
        
        EmailService.send_html_email(
            subject="Test",
            to_email="test@example.com",
            template_name="test.html",
            context={},
            from_email=custom_from
        )
        
        mock_email_class.assert_called_once_with(
            subject="Test",
            body="Test content",
            from_email=custom_from,
            to=["test@example.com"],
        )
    
    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_html_email_template_not_found(self, mock_strip_tags, mock_render_to_string, mock_email_class):
        """Testa erro quando template não é encontrado."""
        from django.template.exceptions import TemplateDoesNotExist
        
        mock_render_to_string.side_effect = TemplateDoesNotExist("Template not found")
        
        with pytest.raises(TemplateDoesNotExist):
            EmailService.send_html_email(
                subject="Test",
                to_email="test@example.com",
                template_name="inexistent.html",
                context={}
            )
    
    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_html_email_email_send_failure(self, mock_strip_tags, mock_render_to_string, mock_email_class):
        """Testa falha no envio do email."""
        mock_render_to_string.return_value = "<html>Test content</html>"
        mock_strip_tags.return_value = "Test content"
        mock_email_instance = Mock()
        mock_email_instance.send.side_effect = Exception("SMTP connection failed")
        mock_email_class.return_value = mock_email_instance
        
        with pytest.raises(Exception, match="SMTP connection failed"):
            EmailService.send_html_email(
                subject="Test",
                to_email="test@example.com",
                template_name="test.html",
                context={}
            )
    
    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_html_email_empty_context(self, mock_strip_tags, mock_render_to_string, mock_email_class):
        """Testa envio de email com contexto vazio."""
        mock_render_to_string.return_value = "<html>Empty context</html>"
        mock_strip_tags.return_value = "Empty context"
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        EmailService.send_html_email(
            subject="Test",
            to_email="test@example.com",
            template_name="test.html",
            context={}
        )
        
        mock_render_to_string.assert_called_once_with("test.html", {})
        mock_email_instance.send.assert_called_once_with(fail_silently=False)


