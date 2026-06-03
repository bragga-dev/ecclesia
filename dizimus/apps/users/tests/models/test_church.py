"""
Testes de Church e ChurchAddress
──────────────────────────────────
Cobre: banner padrão, banner_url, has_valid_asaas_token, refresh_total_members,
__str__, verificação de CNPJ (via validator) e one-to-one com User.
"""

import pytest
from unittest.mock import patch, PropertyMock
from django.db import IntegrityError
from django.test import override_settings

from .conftest import VALID_CNPJ, INVALID_CNPJ, build_user_data


# ─────────────────────────────────────────────────────────────────────────────
# Church — básico
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchBasic:

    def test_church_criada_com_sucesso(self, church):
        assert church.pk is not None

    def test_str_retorna_nome_completo_do_usuario(self, church):
        assert str(church) == church.user.get_full_name()

    def test_is_verified_falso_por_padrao(self, church):
        assert church.is_verified is False

    def test_total_members_zero_por_padrao(self, church):
        assert church.total_members == 0

    def test_relacao_one_to_one_com_user(self, church_user, church):
        assert church.user == church_user
        assert church_user.church == church

    def test_nao_pode_criar_duas_churches_para_mesmo_user(self, church_user, church):
        from dizimus.apps.users.models.church import Church
        with pytest.raises(IntegrityError):
            Church.objects.create(user=church_user)

    def test_instagram_nulo_por_padrao(self, church):
        assert church.instagram is None

    def test_website_nulo_por_padrao(self, church):
        assert church.website is None

    def test_about_nulo_por_padrao(self, church):
        assert church.about is None


# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchBanner:

    def test_banner_padrao_definido_ao_criar(self, church):
        from dizimus.apps.users.models.church import DEFAULT_CHURCH_BANNER
        assert church.banner.name == DEFAULT_CHURCH_BANNER

    def test_banner_padrao_definido_quando_salvo_sem_banner(self, church):
        from dizimus.apps.users.models.church import DEFAULT_CHURCH_BANNER
        church.banner = None
        church.save()
        church.refresh_from_db()
        assert church.banner.name == DEFAULT_CHURCH_BANNER

    def test_banner_url_retorna_url_padrao_quando_banner_e_padrao(self, church):
        with override_settings(MEDIA_URL="/media/"):
            url = church.banner_url
        assert "default/banner.jpg" in url

    def test_banner_url_retorna_url_do_campo_quando_banner_customizado(self, church):
        church.banner.name = "church_banners/algum-id/banner.jpg"
        mock_url = "https://minio.example.com/church_banners/algum-id/banner.jpg"
        with patch.object(
            type(church.banner), "url",
            new_callable=PropertyMock,
            return_value=mock_url,
        ):
            assert church.banner_url == mock_url

    def test_banner_url_tem_fallback_quando_url_levanta_excecao(self, church):
        church.banner.name = "church_banners/algum-id/banner.jpg"
        with patch.object(
            type(church.banner), "url",
            new_callable=PropertyMock,
            side_effect=Exception("Bucket inacessível"),
        ):
            with override_settings(MEDIA_URL="/media/"):
                url = church.banner_url
        assert "default/banner.jpg" in url


# ─────────────────────────────────────────────────────────────────────────────
# Asaas token
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchAsaasToken:

    def test_has_valid_asaas_token_falso_quando_nulo(self, church):
        church.asaas_token = None
        assert church.has_valid_asaas_token is False

    def test_has_valid_asaas_token_falso_quando_vazio(self, church):
        church.asaas_token = ""
        assert church.has_valid_asaas_token is False

    def test_has_valid_asaas_token_falso_quando_apenas_espacos(self, church):
        church.asaas_token = "   "
        assert church.has_valid_asaas_token is False

    def test_has_valid_asaas_token_verdadeiro_quando_preenchido(self, church):
        church.asaas_token = "acess_token_secreto_123"
        assert church.has_valid_asaas_token is True

    def test_has_valid_asaas_token_verdadeiro_com_token_longo(self, church):
        church.asaas_token = "$" * 200
        assert church.has_valid_asaas_token is True


# ─────────────────────────────────────────────────────────────────────────────
# refresh_total_members
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRefreshTotalMembers:

    def _create_link(self, member, church, status):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        return MemberChurch.objects.create(
            member=member, church=church, status=status
        )

    def test_zero_sem_membros(self, church):
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0

    def test_contabiliza_membros_ativos(self, member, church):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        self._create_link(member, church, MemberChurch.Status.ACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 1

    def test_nao_contabiliza_membros_pendentes(self, member, church):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        self._create_link(member, church, MemberChurch.Status.PENDING)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0

    def test_nao_contabiliza_membros_inativos(self, member, church):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        self._create_link(member, church, MemberChurch.Status.INACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0

    def test_contabiliza_apenas_ativos_misturados(self, db, member, second_member, church):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        self._create_link(member,        church, MemberChurch.Status.ACTIVE)
        self._create_link(second_member, church, MemberChurch.Status.INACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 1

    def test_contabiliza_multiplos_ativos(self, db, member, second_member, church):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        self._create_link(member,        church, MemberChurch.Status.ACTIVE)
        self._create_link(second_member, church, MemberChurch.Status.ACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 2

    def test_atualiza_apos_inativar_membro(self, member, church):
        from dizimus.apps.community.models.member_church_model import MemberChurch
        link = self._create_link(member, church, MemberChurch.Status.ACTIVE)
        church.refresh_total_members()
        assert church.total_members == 1

        link.status = MemberChurch.Status.INACTIVE
        link.save()
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0


# ─────────────────────────────────────────────────────────────────────────────
# CNPJ — validator (chamada direta, sem full_clean de Church)
# ─────────────────────────────────────────────────────────────────────────────

class TestCnpjValidator:

    def test_cnpj_valido_nao_levanta_erro(self):
        from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cnpj
        from django.core.exceptions import ValidationError
        try:
            validate_cnpj(VALID_CNPJ)
        except ValidationError:
            pytest.fail("validate_cnpj levantou ValidationError para CNPJ válido")

    def test_cnpj_invalido_levanta_validation_error(self):
        from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cnpj
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            validate_cnpj(INVALID_CNPJ)

    def test_cnpj_com_formato_incorreto_levanta_validation_error(self):
        from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cnpj
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            validate_cnpj("12345")


# ─────────────────────────────────────────────────────────────────────────────
# ChurchAddress — endereço principal
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchAddressPrincipal:
    """
    Testes adicionais específicos da Church; os comportamentos gerais de
    BaseAddress estão em test_address.py.
    """

    def _addr(self, church, number="1", principal=True):
        from dizimus.apps.users.models.church import ChurchAddress
        from .conftest import build_address_data
        return ChurchAddress.objects.create(
            church=church, **build_address_data(number=number, principal=principal)
        )

    def test_novo_endereco_principal_desativa_o_anterior(self, church):
        a1 = self._addr(church, number="1")
        a2 = self._addr(church, number="2")
        a1.refresh_from_db()
        assert a1.principal is False
        assert a2.principal is True

    def test_endereco_nao_principal_nao_toca_nos_outros(self, church):
        a1 = self._addr(church, number="1")
        a2 = self._addr(church, number="2", principal=False)
        a1.refresh_from_db()
        assert a1.principal is True    # mantido
        assert a2.principal is False