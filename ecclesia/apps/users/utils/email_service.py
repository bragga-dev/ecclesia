# utils/email_service.py
import logging
from typing import Optional, Dict, Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Serviço centralizado para envio de emails."""
    
    @staticmethod
    def send_html_email(subject: str, to_email: str, template_name: str, context: Dict[str, Any], from_email: Optional[str] = None,) -> None:
        """Envia email com HTML e fallback para texto."""
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
            
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Email sent to {to_email} - Subject: {subject}")

