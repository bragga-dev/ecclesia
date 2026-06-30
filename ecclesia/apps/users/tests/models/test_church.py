"""
Testes de Church e ChurchAddress
──────────────────────────────────
Cobre: banner padrão, banner_url, has_valid_asaas_token, refresh_total_members,
__str__, verificação de CNPJ (via validator), one-to-one com User, e slug.
"""

import pytest
from unittest.mock import patch, PropertyMock
from django.db import IntegrityError
from django.test import override_settings
from django.utils.text import slugify

from .conftest import VALID_CNPJ, INVALID_CNPJ, build_user_data, build_address_data


# ─────────────────────────────────────────────────────────────────────────────
# Church — básico
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchBasic:

    def test_church_criada_com_sucesso(self, church):
        assert church.pk is not None

    def test_str_retorna_full_name(self, church):
        assert str(church) == church.full_name

    def test_str_fallback_quando_full_name_vazio(self, db):
        from ecclesia.apps.users.models.church import Church
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(
            email="igreja@teste.com",
            role="church",
        )
        church = Church.objects.create(user=user, full_name="")
        assert str(church) == f"Igreja {church.id}"

    def test_is_verified_falso_por_padrao(self, church):
        assert church.is_verified is False

    def test_total_members_zero_por_padrao(self, church):
        assert church.total_members == 0

    def test_relacao_one_to_one_com_user(self, church_user, church):
        assert church.user == church_user
        assert church_user.church == church
    
    def test_nao_pode_criar_duas_churches_para_mesmo_user(self, church_user, church):
        from ecclesia.apps.users.models.church import Church
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Church.objects.create(user=church_user)
        assert 'user' in exc_info.value.message_dict

    def test_instagram_nulo_por_padrao(self, church):
        assert church.instagram is None

    def test_website_nulo_por_padrao(self, church):
        assert church.website is None

    def test_about_nulo_por_padrao(self, church):
        assert church.about is None

    def test_church_type_padrao_e_independent(self, church):
        from ecclesia.apps.users.models.church import Church
        assert church.church_type == Church.ChurchType.INDEPENDENT

    def test_parent_church_nulo_por_padrao(self, church):
        assert church.parent_church is None


# ─────────────────────────────────────────────────────────────────────────────
# Church — slug
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchSlug:

    def test_slug_gerado_ao_criar(self, church):
        assert church.slug != ""
        assert church.slug is not None

    def test_slug_baseado_no_full_name(self, church):
        # full_name = "Igreja Batista" → "igreja-batista"
        assert church.slug == slugify(church.full_name)

    def test_slug_unico_para_nomes_iguais(self, db):
        from ecclesia.apps.users.models.church import Church
        from ecclesia.apps.users.models.user import User
        
        u1 = User.objects.create_user(email="igreja1@teste.com", role="church")
        u2 = User.objects.create_user(email="igreja2@teste.com", role="church")
        
        c1 = Church.objects.create(user=u1, full_name="Igreja da Paz")
        c2 = Church.objects.create(user=u2, full_name="Igreja da Paz")
        
        assert c1.slug != c2.slug
        assert c2.slug.startswith("igreja-da-paz")

    def test_slug_usa_uuid_quando_full_name_vazio(self, db):
        from ecclesia.apps.users.models.church import Church
        from ecclesia.apps.users.models.user import User
        
        user = User.objects.create_user(email="igreja@teste.com", role="church")
        church = Church.objects.create(user=user, full_name="")
        
        # O slug deve ser o ID (que é UUID) já que não tem nome
        assert church.slug == str(church.id)

    def test_slug_regenerado_ao_trocar_full_name(self, church):
        slug_original = church.slug
        church.full_name = "Igreja Batista da Paz"
        church.save()
        church.refresh_from_db()
        assert church.slug != slug_original
        assert "igreja-batista-da-paz" in church.slug

    def test_slug_nao_alterado_sem_mudanca_de_nome(self, church):
        slug_original = church.slug
        church.phone = "+55 11 99999-8888"
        church.save()
        church.refresh_from_db()
        assert church.slug == slug_original


# ─────────────────────────────────────────────────────────────────────────────
# Church — has_name_changed
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchHasNameChanged:

    def test_falso_em_nova_instancia_nao_salva(self, db):
        from ecclesia.apps.users.models.church import Church
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(email="novo@teste.com", role="church")
        church = Church(user=user, full_name="Igreja Nova")
        # _state.adding=True → nunca considera como alteração
        assert church.has_name_changed() is False

    def test_falso_quando_nome_nao_muda(self, church):
        church.full_name = "Igreja Batista"
        assert church.has_name_changed() is False

    def test_verdadeiro_quando_full_name_muda(self, church):
        church.full_name = "Igreja Batista da Paz"
        assert church.has_name_changed() is True


# ─────────────────────────────────────────────────────────────────────────────
# Church — banner
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchBanner:

    def test_banner_padrao_definido_ao_criar(self, church):
        from ecclesia.apps.users.models.church import DEFAULT_CHURCH_BANNER
        assert church.banner.name == DEFAULT_CHURCH_BANNER

    def test_banner_padrao_definido_quando_salvo_sem_banner(self, church):
        from ecclesia.apps.users.models.church import DEFAULT_CHURCH_BANNER
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
# Church — Asaas token
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
# Church — refresh_total_members
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRefreshTotalMembers:

    def _create_link(self, member, church, status):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        return MemberChurch.objects.create(
            member=member, church=church, status=status
        )

    def test_zero_sem_membros(self, church):
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0

    def test_contabiliza_membros_ativos(self, member, church):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        self._create_link(member, church, MemberChurch.Status.ACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 1

    def test_nao_contabiliza_membros_pendentes(self, member, church):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        self._create_link(member, church, MemberChurch.Status.PENDING)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0

    def test_nao_contabiliza_membros_inativos(self, member, church):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        self._create_link(member, church, MemberChurch.Status.INACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0

    def test_contabiliza_apenas_ativos_misturados(self, db, member, second_member, church):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        self._create_link(member,        church, MemberChurch.Status.ACTIVE)
        self._create_link(second_member, church, MemberChurch.Status.INACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 1

    def test_contabiliza_multiplos_ativos(self, db, member, second_member, church):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        self._create_link(member,        church, MemberChurch.Status.ACTIVE)
        self._create_link(second_member, church, MemberChurch.Status.ACTIVE)
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 2

    def test_atualiza_apos_inativar_membro(self, member, church):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        link = self._create_link(member, church, MemberChurch.Status.ACTIVE)
        church.refresh_total_members()
        assert church.total_members == 1

        link.status = MemberChurch.Status.INACTIVE
        link.save()
        church.refresh_total_members()
        church.refresh_from_db()
        assert church.total_members == 0


# ─────────────────────────────────────────────────────────────────────────────
# Church — CNPJ (validator)
# ─────────────────────────────────────────────────────────────────────────────

class TestCnpjValidator:

    def test_cnpj_valido_nao_levanta_erro(self):
        from ecclesia.apps.users.validators.validate_cpf_cnpj import validate_cnpj
        from django.core.exceptions import ValidationError
        try:
            validate_cnpj(VALID_CNPJ)
        except ValidationError:
            pytest.fail("validate_cnpj levantou ValidationError para CNPJ válido")

    def test_cnpj_invalido_levanta_validation_error(self):
        from ecclesia.apps.users.validators.validate_cpf_cnpj import validate_cnpj
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            validate_cnpj(INVALID_CNPJ)

    def test_cnpj_com_formato_incorreto_levanta_validation_error(self):
        from ecclesia.apps.users.validators.validate_cpf_cnpj import validate_cnpj
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            validate_cnpj("12345")


# ─────────────────────────────────────────────────────────────────────────────
# Church — phone
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchPhone:

    def test_normalize_phone_retorna_e164(self):
        from ecclesia.apps.users.models.church import Church
        resultado = Church.normalize_phone("+55 11 99999-8888")
        assert resultado == "+5511999998888"

    def test_normalize_phone_com_telefone_sem_formatacao(self):
        from ecclesia.apps.users.models.church import Church
        resultado = Church.normalize_phone("11999998888")
        assert resultado == "+5511999998888"

    def test_phone_pode_ser_definido_com_formato_internacional(self, church):
        church.phone = "+55 11 99999-8888"
        church.save()
        church.refresh_from_db()
        # O campo armazena no formato E.164
        assert str(church.phone) == "+5511999998888"


# ─────────────────────────────────────────────────────────────────────────────
# ChurchAddress
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchAddress:

    def test_endereco_criado_com_sucesso(self, church):
        from ecclesia.apps.users.models.church import ChurchAddress
        addr = ChurchAddress.objects.create(
            church=church,
            **build_address_data()
        )
        assert addr.pk is not None

    def test_endereco_principal_por_padrao(self, church):
        from ecclesia.apps.users.models.church import ChurchAddress
        addr = ChurchAddress.objects.create(
            church=church,
            **build_address_data()
        )
        assert addr.principal is True

    def test_novo_endereco_principal_desativa_anterior(self, church):
        from ecclesia.apps.users.models.church import ChurchAddress
        addr1 = ChurchAddress.objects.create(
            church=church,
            **build_address_data(number="1")
        )
        addr2 = ChurchAddress.objects.create(
            church=church,
            **build_address_data(number="2", principal=True)
        )
        addr1.refresh_from_db()
        assert addr1.principal is False
        assert addr2.principal is True

    def test_apenas_um_principal_por_church(self, church):
        from ecclesia.apps.users.models.church import ChurchAddress
        for n in ("10", "20", "30"):
            ChurchAddress.objects.create(
                church=church,
                **build_address_data(number=n)
            )
        total_principais = ChurchAddress.objects.filter(
            church=church, principal=True
        ).count()
        assert total_principais == 1

    def test_str_retorna_endereco_formatado(self, church):
        from ecclesia.apps.users.models.church import ChurchAddress
        addr = ChurchAddress.objects.create(
            church=church,
            **build_address_data(
                road="Praça da Sé",
                number="1",
                city="São Paulo",
                state="SP"
            )
        )
        assert str(addr) == "Praça da Sé, 1 - São Paulo/SP"

    def test_slug_gerado_ao_criar(self, church):
        from ecclesia.apps.users.models.church import ChurchAddress
        addr = ChurchAddress.objects.create(
            church=church,
            **build_address_data()
        )
        assert addr.slug != ""
