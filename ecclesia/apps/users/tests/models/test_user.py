"""
Testes do model User
─────────────────────
Cobre: properties (is_member, is_church, photo_url), helpers (email_user, 
normalize_phone), __str__, e campos básicos.
"""

import pytest
from unittest.mock import patch, PropertyMock
from django.test import override_settings

from .conftest import build_user_data, VALID_PHONE


# ─────────────────────────────────────────────────────────────────────────────
# Campos básicos
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserBasic:

    def test_str_retorna_email(self, member_user):
        assert str(member_user) == member_user.email

    def test_email_e_normalizado(self):
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data(
            email="Usuario@TESTE.COM",
        ))
        # Django normaliza apenas o domínio para minúsculas
        assert user.email == "Usuario@teste.com"

    def test_date_joined_preenchido_ao_criar(self, member_user):
        assert member_user.date_joined is not None

    def test_last_login_preenchido_ao_criar(self, member_user):
        assert member_user.last_login is not None

    def test_created_at_preenchido_ao_criar(self, member_user):
        assert member_user.created_at is not None

    def test_updated_at_preenchido_ao_criar(self, member_user):
        assert member_user.updated_at is not None

    def test_updated_at_atualizado_ao_salvar(self, member_user):
        updated_original = member_user.updated_at
        member_user.is_active = True
        member_user.save()
        member_user.refresh_from_db()
        assert member_user.updated_at > updated_original


# ─────────────────────────────────────────────────────────────────────────────
# Foto — save() e photo_url
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserPhoto:

    def test_foto_padrao_definida_ao_criar(self, member_user):
        from ecclesia.apps.users.models.user import DEFAULT_USER_PHOTO
        assert member_user.photo.name == DEFAULT_USER_PHOTO

    def test_foto_padrao_definida_quando_salvo_sem_foto(self, member_user):
        from ecclesia.apps.users.models.user import DEFAULT_USER_PHOTO
        member_user.photo = None
        member_user.save()
        member_user.refresh_from_db()
        assert member_user.photo.name == DEFAULT_USER_PHOTO

    def test_photo_url_retorna_url_padrao_quando_foto_e_padrao(self, member_user):
        with override_settings(MEDIA_URL="/media/"):
            url = member_user.photo_url
        assert "default/user_img.jpg" in url

    def test_photo_url_retorna_url_do_campo_quando_foto_customizada(self, member_user):
        """Quando a foto não é a padrão, photo_url deve retornar photo.url."""
        member_user.photo.name = "photos/algum-uuid/photo.jpg"
        mock_url = "https://minio.example.com/photos/algum-uuid/photo.jpg"
        with patch.object(
            type(member_user.photo), "url",
            new_callable=PropertyMock,
            return_value=mock_url,
        ):
            assert member_user.photo_url == mock_url

    def test_photo_url_tem_fallback_quando_photo_url_levanta_excecao(self, member_user):
        """Se photo.url lançar exceção, photo_url retorna URL padrão."""
        member_user.photo.name = "photos/algum-uuid/photo.jpg"
        with patch.object(
            type(member_user.photo), "url",
            new_callable=PropertyMock,
            side_effect=Exception("Bucket inacessível"),
        ):
            with override_settings(MEDIA_URL="/media/"):
                url = member_user.photo_url
        assert "default/user_img.jpg" in url


# ─────────────────────────────────────────────────────────────────────────────
# Properties booleanas
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserProperties:

    def test_is_member_verdadeiro_para_member(self, member_user):
        assert member_user.is_member is True

    def test_is_member_falso_para_church(self, church_user):
        assert church_user.is_member is False

    def test_is_church_verdadeiro_para_church(self, church_user):
        assert church_user.is_church is True

    def test_is_church_falso_para_member(self, member_user):
        assert member_user.is_church is False


# ─────────────────────────────────────────────────────────────────────────────
# Métodos auxiliares
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserHelpers:

    def test_email_user_chama_send_mail(self, member_user):
        with patch("ecclesia.apps.users.models.user.send_mail") as mock_send:
            member_user.email_user("Assunto", "Corpo")
            mock_send.assert_called_once_with(
                "Assunto", "Corpo", None, [member_user.email]
            )

    def test_normalize_phone_retorna_e164(self):
        from ecclesia.apps.users.models.member import Member
        resultado = Member.normalize_phone("+55 11 99999-8888")
        assert resultado == "+5511999998888"

    def test_normalize_phone_com_telefone_sem_formatacao(self):
        from ecclesia.apps.users.models.member import Member
        resultado = Member.normalize_phone("11999998888")
        assert resultado == "+5511999998888"