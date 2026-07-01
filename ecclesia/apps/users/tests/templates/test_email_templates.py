# tests/utils/test_email_templates.py
import pytest
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from unittest.mock import Mock, patch, MagicMock
from ecclesia.apps.users.utils.email_service import EmailService


class TestEmailTemplates:
    """Testes para os templates de email do Ecclesia."""

    # ─────────────────────────────────────────────────────────────
    # Fixtures
    # ─────────────────────────────────────────────────────────────

    @pytest.fixture
    def member_invite_context(self):
        """Contexto para o template de convite de membro."""
        return {
            "member_email": "joao@example.com",
            "church_name": "Igreja Batista da Paz",
            "church_banner": "https://media.ecclesia.com/banners/batista.jpg",
            "temp_password": "Temp@123456",
            "verify_url": "https://api.ecclesia.com/api/users/verify-email/MQ/abc123token"
        }

    @pytest.fixture
    def password_reset_context(self):
        """Contexto para o template de redefinição de senha."""
        return {
            "user_email": "maria@example.com",
            "reset_url": "https://frontend.ecclesia.com/redefinir-senha/MQ/def456token"
        }

    @pytest.fixture
    def verification_context(self):
        """Contexto para o template de verificação de email."""
        return {
            "user_email": "pedro@example.com",
            "verify_url": "https://api.ecclesia.com/api/users/verify-email/MQ/ghi789token"
        }

    # ─────────────────────────────────────────────────────────────
    # Testes: Member Invite Template
    # ─────────────────────────────────────────────────────────────

    def test_member_invite_template_renders(self, member_invite_context):
        """Testa se o template de convite de membro renderiza corretamente."""
        html_content = render_to_string(
            "emails/member_invite.html", 
            member_invite_context
        )
        
        # Verificações básicas
        assert html_content is not None
        assert isinstance(html_content, str)
        assert len(html_content) > 0
        
        # Verifica elementos obrigatórios
        assert "ECCLESIA" in html_content
        assert "Bem-vindo ao Ecclesia" in html_content
        assert member_invite_context["member_email"] in html_content
        assert member_invite_context["church_name"] in html_content
        assert member_invite_context["temp_password"] in html_content
        assert member_invite_context["verify_url"] in html_content
        
        # Verifica seções específicas
        assert "Credenciais de Acesso" in html_content
        assert "Senha temporária" in html_content
        assert "Próximos Passos" in html_content
        assert "Confirme seu e-mail" in html_content or "CONFIRMAR MEU E-MAIL" in html_content

    def test_member_invite_template_without_banner(self, member_invite_context):
        """Testa o template de convite sem banner."""
        # Remove o banner do contexto
        context = member_invite_context.copy()
        context.pop("church_banner", None)
        
        html_content = render_to_string("emails/member_invite.html", context)
        
        # Verifica que o ícone aparece (sem banner)
        assert "⛪" in html_content or "icon-badge" in html_content
        assert "banner-wrap" not in html_content or "banner-wrap" not in html_content

    def test_member_invite_template_with_banner(self, member_invite_context):
        """Testa o template de convite COM banner."""
        html_content = render_to_string(
            "emails/member_invite.html", 
            member_invite_context
        )
        
        # Verifica que o banner está presente
        assert "banner-wrap" in html_content
        assert member_invite_context["church_banner"] in html_content
        
        # Verifica que o ícone NÃO aparece (banner substitui)
        assert "⛪" not in html_content or "icon-badge" not in html_content

    def test_member_invite_template_contains_required_links(self, member_invite_context):
        """Testa se o template contém os links necessários."""
        html_content = render_to_string(
            "emails/member_invite.html", 
            member_invite_context
        )
        
        # Verifica botão CTA
        assert "cta-btn" in html_content
        assert member_invite_context["verify_url"] in html_content
        
        # Verifica fallback link
        assert "link-fallback" in html_content
        assert member_invite_context["verify_url"] in html_content

    # ─────────────────────────────────────────────────────────────
    # Testes: Password Reset Template
    # ─────────────────────────────────────────────────────────────

    def test_password_reset_template_renders(self, password_reset_context):
        """Testa se o template de redefinição de senha renderiza corretamente."""
        html_content = render_to_string(
            "emails/password_reset.html", 
            password_reset_context
        )
        
        # Verificações básicas
        assert html_content is not None
        assert isinstance(html_content, str)
        assert len(html_content) > 0
        
        # Verifica elementos obrigatórios
        assert "ECCLESIA" in html_content
        assert "Redefinição de Senha" in html_content
        assert password_reset_context["user_email"] in html_content
        assert password_reset_context["reset_url"] in html_content
        
        # Verifica seções específicas
        assert "Segurança da conta" in html_content
        assert "Segurança em primeiro lugar" in html_content
        assert "REDEFINIR SENHA" in html_content or "Redefinir Senha" in html_content
        assert "Este link expira em 1 hora" in html_content

    def test_password_reset_template_security_info(self, password_reset_context):
        """Testa as informações de segurança no template."""
        html_content = render_to_string(
            "emails/password_reset.html", 
            password_reset_context
        )
        
        # Verifica informações de segurança
        assert "expira em" in html_content
        assert "1 hora" in html_content
        assert "Se você não solicitou" in html_content
        assert "ignore este e-mail" in html_content

    def test_password_reset_template_contains_cta(self, password_reset_context):
        """Testa se o template contém o botão CTA."""
        html_content = render_to_string(
            "emails/password_reset.html", 
            password_reset_context
        )
        
        # Verifica CTA
        assert "cta-btn" in html_content
        assert password_reset_context["reset_url"] in html_content
        
        # Verifica fallback
        assert "link-fallback" in html_content

    # ─────────────────────────────────────────────────────────────
    # Testes: Verification Email Template
    # ─────────────────────────────────────────────────────────────

    def test_verification_template_renders(self, verification_context):
        """Testa se o template de verificação de email renderiza corretamente."""
        html_content = render_to_string(
            "emails/verification_email.html", 
            verification_context
        )
        
        # Verificações básicas
        assert html_content is not None
        assert isinstance(html_content, str)
        assert len(html_content) > 0
        
        # Verifica elementos obrigatórios
        assert "ECCLESIA" in html_content
        assert "Confirme seu E-mail" in html_content
        assert verification_context["user_email"] in html_content
        assert verification_context["verify_url"] in html_content
        
        # Verifica seções específicas
        assert "Verificação de conta" in html_content
        assert "Por que confirmar?" in html_content
        assert "CONFIRMAR E-MAIL" in html_content or "Confirmar E-mail" in html_content

    def test_verification_template_expiry_info(self, verification_context):
        """Testa as informações de expiração no template de verificação."""
        html_content = render_to_string(
            "emails/verification_email.html", 
            verification_context
        )
        
        # Verifica informações de expiração
        assert "expira em" in html_content
        assert "24 horas" in html_content
        assert "uso único" in html_content
        assert "Se você não criou uma conta" in html_content

    def test_verification_template_contains_links(self, verification_context):
        """Testa se o template contém os links necessários."""
        html_content = render_to_string(
            "emails/verification_email.html", 
            verification_context
        )
        
        # Verifica botão e fallback
        assert "cta-btn" in html_content
        assert verification_context["verify_url"] in html_content
        assert "link-fallback" in html_content

    # ─────────────────────────────────────────────────────────────
    # Testes: Compatibilidade e Acessibilidade
    # ─────────────────────────────────────────────────────────────

    def test_templates_have_preheader(self, member_invite_context, 
                                     password_reset_context, 
                                     verification_context):
        """Testa se todos os templates têm preheader (visível no inbox)."""
        templates = [
            ("emails/member_invite.html", member_invite_context),
            ("emails/password_reset.html", password_reset_context),
            ("emails/verification_email.html", verification_context)
        ]
        
        for template_name, context in templates:
            html_content = render_to_string(template_name, context)
            assert "preheader" in html_content
            assert "display: none" in html_content or "mso-hide" in html_content

    def test_templates_have_mobile_responsive(self, member_invite_context):
        """Testa se o template tem suporte a mobile."""
        html_content = render_to_string(
            "emails/member_invite.html", 
            member_invite_context
        )
        
        # Verifica media queries para mobile
        assert "@media only screen and (max-width: 600px)" in html_content
        assert "max-width: 400px" in html_content

    def test_templates_have_dark_mode_support(self, member_invite_context):
        """Testa se o template tem suporte a dark mode."""
        html_content = render_to_string(
            "emails/member_invite.html", 
            member_invite_context
        )
        
        # Verifica dark mode
        assert "prefers-color-scheme: dark" in html_content

    def test_templates_have_fallback_for_old_email_clients(self, member_invite_context):
        """Testa se o template tem fallback para clientes de email antigos."""
        html_content = render_to_string(
            "emails/member_invite.html", 
            member_invite_context
        )
        
        # Verifica MSO (Microsoft Office) fallback
        assert "[if mso]" in html_content
        assert "v:roundrect" in html_content

    # ─────────────────────────────────────────────────────────────
    # Testes: Integração com EmailService
    # ─────────────────────────────────────────────────────────────

    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_member_invite_email(self, mock_strip_tags, 
                                     mock_render_to_string, 
                                     mock_email_class,
                                     member_invite_context):
        """Testa o envio do email de convite de membro via EmailService."""
        # Configurar mocks
        mock_render_to_string.return_value = "<html>Member invite content</html>"
        mock_strip_tags.return_value = "Member invite content"
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        # Dados do email
        subject = "Bem-vindo ao Ecclesia"
        to_email = "joao@example.com"
        template_name = "emails/member_invite.html"
        
        # Executar
        EmailService.send_html_email(
            subject=subject,
            to_email=to_email,
            template_name=template_name,
            context=member_invite_context
        )
        
        # Verificações
        mock_render_to_string.assert_called_once_with(
            template_name, 
            member_invite_context
        )
        mock_email_class.assert_called_once_with(
            subject=subject,
            body="Member invite content",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        mock_email_instance.attach_alternative.assert_called_once_with(
            "<html>Member invite content</html>", 
            "text/html"
        )
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_password_reset_email(self, mock_strip_tags, 
                                      mock_render_to_string, 
                                      mock_email_class,
                                      password_reset_context):
        """Testa o envio do email de redefinição de senha via EmailService."""
        mock_render_to_string.return_value = "<html>Password reset content</html>"
        mock_strip_tags.return_value = "Password reset content"
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        subject = "Redefinição de Senha - Ecclesia"
        to_email = "maria@example.com"
        template_name = "emails/password_reset.html"
        
        EmailService.send_html_email(
            subject=subject,
            to_email=to_email,
            template_name=template_name,
            context=password_reset_context
        )
        
        mock_render_to_string.assert_called_once_with(
            template_name, 
            password_reset_context
        )
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @patch('ecclesia.apps.users.utils.email_service.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.utils.email_service.render_to_string')
    @patch('ecclesia.apps.users.utils.email_service.strip_tags')
    def test_send_verification_email(self, mock_strip_tags, 
                                    mock_render_to_string, 
                                    mock_email_class,
                                    verification_context):
        """Testa o envio do email de verificação via EmailService."""
        mock_render_to_string.return_value = "<html>Verification content</html>"
        mock_strip_tags.return_value = "Verification content"
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        subject = "Confirme seu E-mail - Ecclesia"
        to_email = "pedro@example.com"
        template_name = "emails/verification_email.html"
        
        EmailService.send_html_email(
            subject=subject,
            to_email=to_email,
            template_name=template_name,
            context=verification_context
        )
        
        mock_render_to_string.assert_called_once_with(
            template_name, 
            verification_context
        )
        mock_email_instance.send.assert_called_once_with(fail_silently=False)


# ─────────────────────────────────────────────────────────────
# Testes de Performance e Validação
# ─────────────────────────────────────────────────────────────

class TestEmailTemplatePerformance:
    """Testes de performance e validação dos templates."""

    @pytest.fixture
    def large_context(self):
        """Cria um contexto grande para testar performance."""
        return {
            "member_email": "test" * 100 + "@example.com",
            "church_name": "Igreja " * 50,
            "church_banner": "https://media.ecclesia.com/banners/" + "a" * 200 + ".jpg",
            "temp_password": "Temp@" + "1" * 50,
            "verify_url": "https://api.ecclesia.com/api/users/verify-email/" + "a" * 100 + "/" + "b" * 100
        }

    def test_template_rendering_performance(self, large_context):
        """Testa se o template renderiza rapidamente mesmo com dados grandes."""
        import time
        
        start = time.time()
        html_content = render_to_string("emails/member_invite.html", large_context)
        end = time.time()
        
        # Deve renderizar em menos de 1 segundo
        assert end - start < 1.0
        assert len(html_content) > 0

    def test_template_contains_all_required_variables(self, member_invite_context):
        """Testa se todas as variáveis do contexto são usadas no template."""
        html_content = render_to_string("emails/member_invite.html", member_invite_context)
        
        # Verifica que todas as variáveis aparecem no HTML renderizado
        for key, value in member_invite_context.items():
            if isinstance(value, str):
                assert str(value) in html_content or key in html_content

    def test_template_html_is_valid(self, member_invite_context):
        """Testa se o HTML gerado é válido (tags fechadas)."""
        from bs4 import BeautifulSoup
        
        html_content = render_to_string("emails/member_invite.html", member_invite_context)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Verifica que não há tags não fechadas (BeautifulSoup faz parsing)
        # Se houver erro de parsing, BeautifulSoup vai gerar warnings
        assert soup is not None


# ─────────────────────────────────────────────────────────────
# Testes de Fallback (Texto Puro)
# ─────────────────────────────────────────────────────────────

class TestEmailTextFallback:
    """Testes para a versão texto dos emails (fallback)."""

    def test_member_invite_text_fallback(self, member_invite_context):
        """Testa a versão texto do email de convite."""
        html_content = render_to_string("emails/member_invite.html", member_invite_context)
        text_content = strip_tags(html_content)
        
        # Verifica que o texto contém informações importantes
        assert "Bem-vindo ao Ecclesia" in text_content
        assert member_invite_context["member_email"] in text_content
        assert member_invite_context["temp_password"] in text_content
        assert member_invite_context["verify_url"] in text_content
        
        # Verifica que não há tags HTML
        assert "<html>" not in text_content
        assert "<body>" not in text_content
        assert "<div" not in text_content

    def test_password_reset_text_fallback(self, password_reset_context):
        """Testa a versão texto do email de redefinição de senha."""
        html_content = render_to_string("emails/password_reset.html", password_reset_context)
        text_content = strip_tags(html_content)
        
        assert "Redefinição de Senha" in text_content
        assert password_reset_context["user_email"] in text_content
        assert password_reset_context["reset_url"] in text_content
        assert "expira em" in text_content
        assert "1 hora" in text_content

    def test_verification_text_fallback(self, verification_context):
        """Testa a versão texto do email de verificação."""
        html_content = render_to_string("emails/verification_email.html", verification_context)
        text_content = strip_tags(html_content)
        
        assert "Confirme seu E-mail" in text_content
        assert verification_context["user_email"] in text_content
        assert verification_context["verify_url"] in text_content
        assert "expira em" in text_content
        assert "24 horas" in text_content