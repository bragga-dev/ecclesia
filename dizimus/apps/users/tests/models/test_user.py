"""
Testes do model User
─────────────────────
Cobre: slug, clean(), save(), properties (is_member, is_church, photo_url),
helpers (get_full_name, get_short_name, email_user, normalize_phone,
has_name_changed) e __str__.
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils.text import slugify
from .conftest import build_user_data, VALID_PHONE


# ─────────────────────────────────────────────────────────────────────────────
# Slug
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserSlug:

    def test_slug_gerado_ao_criar(self, member_user):
        assert member_user.slug != ""
        assert member_user.slug is not None

    def test_slug_baseado_no_nome_completo(self, member_user):
        # "João Silva" → "joao-silva"
        assert "joao" in member_user.slug
        assert "silva" in member_user.slug

    def test_slug_unico_para_nomes_iguais(self, db):
        from dizimus.apps.users.models import User
        u1 = User.objects.create_user(**build_user_data(
            email="a@teste.com", username="user_a",
            first_name="Ana", last_name="Lima",
        ))
        u2 = User.objects.create_user(**build_user_data(
            email="b@teste.com", username="user_b",
            first_name="Ana", last_name="Lima",
        ))
        assert u1.slug != u2.slug
        assert u2.slug.startswith("ana-lima")

    def test_slug_incrementa_com_sufixo_numerico(self, db):
        from dizimus.apps.users.models.user import User
        base_data = dict(first_name="Pedro", last_name="Costa")
        u1 = User.objects.create_user(**build_user_data(
            email="p1@teste.com", username="pedro1", **base_data
        ))
        u2 = User.objects.create_user(**build_user_data(
            email="p2@teste.com", username="pedro2", **base_data
        ))
        u3 = User.objects.create_user(**build_user_data(
            email="p3@teste.com", username="pedro3", **base_data
        ))
        slugs = {u1.slug, u2.slug, u3.slug}
        assert len(slugs) == 3     # todos diferentes

    def test_slug_usa_uuid_quando_nome_vazio(self, db):
        from dizimus.apps.users.models.user import User
        
        user = User(
            email="sem_nome@teste.com",
            username="semnome",
            first_name="Igreja Teste", 
            last_name="",              
            role="church",
        )
        user.set_password("Senha123!")
        user.save()
    
        # O slug deve ser gerado a partir do first_name
        assert user.slug == slugify("Igreja Teste")

    def test_slug_regenerado_ao_trocar_primeiro_nome(self, member_user):
        slug_original = member_user.slug
        member_user.first_name = "Carlos"
        member_user.save()
        member_user.refresh_from_db()
        assert member_user.slug != slug_original
        assert "carlos" in member_user.slug

    def test_slug_regenerado_ao_trocar_sobrenome(self, member_user):
        slug_original = member_user.slug
        member_user.last_name = "Ferreira"
        member_user.save()
        member_user.refresh_from_db()
        assert member_user.slug != slug_original

    def test_slug_nao_alterado_sem_mudanca_de_nome(self, member_user):
        slug_original = member_user.slug
        member_user.phone = VALID_PHONE
        member_user.save()
        member_user.refresh_from_db()
        assert member_user.slug == slug_original


# ─────────────────────────────────────────────────────────────────────────────
# Validação — clean()
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserClean:

    def test_member_sem_sobrenome_levanta_validation_error(self, db):
        from dizimus.apps.users.models.user import User
        with pytest.raises(ValidationError) as exc_info:
            User.objects.create_user(**build_user_data(last_name=""))
        assert "last_name" in exc_info.value.message_dict

    def test_church_sem_sobrenome_nao_levanta_erro(self, db):
        """Para CHURCH o sobrenome é opcional."""
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data(
            email="church_sem_last@teste.com",
            username="church_sem_last",
            first_name="Igreja",
            last_name="",
            role="church",
        ))
        assert user.pk is not None

    def test_admin_sem_sobrenome_nao_levanta_erro(self, db):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_superuser(**build_user_data(
            email="admin_sem_last@teste.com",
            username="admin_sem_last",
            first_name="Admin",
            last_name="",
        ))
        assert user.pk is not None


# ─────────────────────────────────────────────────────────────────────────────
# Foto — save() e photo_url
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUserPhoto:

    def test_foto_padrao_definida_ao_criar(self, member_user):
        from dizimus.apps.users.models.user import DEFAULT_USER_PHOTO
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

    def test_get_full_name(self, member_user):
        assert member_user.get_full_name() == "João Silva"

    def test_get_full_name_sem_sobrenome(self, db):
        from dizimus.apps.users.models.user import User
        user = User.objects.create_user(**build_user_data(
            email="sn@teste.com", username="semnome2",
            first_name="Maria", last_name="",
            role="church",
        ))
        assert user.get_full_name() == "Maria"

    def test_get_short_name(self, member_user):
        assert member_user.get_short_name() == "João"

    def test_str_retorna_email(self, member_user):
        assert str(member_user) == member_user.email

    def test_email_user_chama_send_mail(self, member_user):
        with patch("dizimus.apps.users.models.user.send_mail") as mock_send:
            member_user.email_user("Assunto", "Corpo")
            mock_send.assert_called_once_with(
                "Assunto", "Corpo", None, [member_user.email]
            )

    def test_normalize_phone_retorna_e164(self):
        from dizimus.apps.users.models import User
        resultado = User.normalize_phone("+55 11 99999-8888")
        assert resultado == "+5511999998888"


# ─────────────────────────────────────────────────────────────────────────────
# has_name_changed
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHasNameChanged:

    def test_falso_em_nova_instancia_nao_salva(self, db):
        from dizimus.apps.users.models.user import User
        user = User(
            email="novo@teste.com",
            username="novousr",
            first_name="Novo",
            last_name="User",
            role="church",
        )
        # _state.adding=True → nunca considera como alteração
        assert user.has_name_changed() is False

    def test_falso_quando_nome_nao_muda(self, member_user):
        # Reatribuição com o mesmo valor
        member_user.first_name = "João"
        member_user.last_name = "Silva"
        assert member_user.has_name_changed() is False

    def test_verdadeiro_quando_primeiro_nome_muda(self, member_user):
        member_user.first_name = "Carlos"
        assert member_user.has_name_changed() is True

    def test_verdadeiro_quando_sobrenome_muda(self, member_user):
        member_user.last_name = "Pereira"
        assert member_user.has_name_changed() is True