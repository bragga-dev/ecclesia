# utils/token_service.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

class TokenService:
    """Serviço para geração de tokens e URLs."""
    
    @staticmethod
    def generate_verification_data(user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token
    
    @staticmethod
    def build_verification_url(uid, token):
        return f"{settings.BACKEND_URL}/api/users/verify-email/{uid}/{token}"
    
    @staticmethod
    def build_password_reset_url(uid, token):
        return f"{settings.FRONTEND_URL}/redefinir-senha/{uid}/{token}"