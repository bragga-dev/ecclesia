"""
Testes de Member e MemberAddress
─────────────────────────────────
Cobre: validação de data_of_birth, __str__, unicidade de vínculo, 
slug, phone normalization, e campos básicos.
"""

import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify

from .conftest import VALID_CPF, VALID_PHONE, build_user_data, build_address_data


# ─────────────────────────────────────────────────────────────────────────────
# Member — básico
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMember:

    def test_member_criado_com_sucesso(self, member):
        assert member.pk is not None

    def test_str_retorna_primeiro_nome(self, member):
        assert str(member) == member.first_name

    def test_str_fallback_quando_primeiro_nome_vazio(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(
            email="membro@teste.com",
            role="member",
        )
        member = Member.objects.create(user=user, first_name="", last_name="")
        assert str(member) == f"Membro {member.id}"

    def test_get_full_name_retorna_nome_completo(self, member):
        assert member.get_full_name() == "João Silva"

    def test_get_full_name_sem_sobrenome(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(email="maria@teste.com", role="member")
        member = Member.objects.create(user=user, first_name="Maria", last_name="")
        assert member.get_full_name() == "Maria"

    def test_get_full_name_fallback_quando_vazio(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(email="anon@teste.com", role="member")
        member = Member.objects.create(user=user, first_name="", last_name="")
        assert member.get_full_name() == f"Membro {member.id}"

    def test_relacao_one_to_one_com_user(self, member_user, member):
        assert member.user == member_user
        assert member_user.member == member

    def test_nao_pode_criar_dois_members_para_mesmo_user(self, db, member_user, member):
        from ecclesia.apps.users.models.member import Member
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Member.objects.create(user=member_user)
        assert 'user' in exc_info.value.message_dict

    def test_member_criado_sem_cpf(self, member):
        assert member.cpf is None

    def test_member_criado_sem_data_nascimento(self, member):
        assert member.date_of_birth is None

    def test_member_criado_sem_telefone(self, member):
        assert member.phone == ""


# ─────────────────────────────────────────────────────────────────────────────
# Member — CPF
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberCpf:

    def test_member_com_cpf_valido(self, member):
        member.cpf = VALID_CPF
        member.full_clean()   # não deve lançar

    def test_member_com_cpf_invalido_levanta_validation_error(self, member):
        from ecclesia.apps.users.validators.validate_cpf_cnpj import validate_cpf
        with pytest.raises(ValidationError):
            validate_cpf("111.111.111-11")

    def test_cpf_unicidade(self, db, member):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        from django.core.exceptions import ValidationError
        
        member.cpf = VALID_CPF
        member.save()

        outro_user = User.objects.create_user(
            email="outro@teste.com",
            role="member",
        )
        outro_member = Member(user=outro_user, cpf=VALID_CPF)
        with pytest.raises(ValidationError) as exc_info:
            outro_member.save()
        assert 'cpf' in exc_info.value.message_dict


# ─────────────────────────────────────────────────────────────────────────────
# Member — data de nascimento
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberDateOfBirth:

    def test_clean_data_nascimento_futura_levanta_validation_error(self, member):
        member.date_of_birth = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            member.clean()
        assert "date_of_birth" in exc_info.value.message_dict

    def test_clean_data_nascimento_hoje_nao_levanta_erro(self, member):
        """Hoje não é > localdate() → passa."""
        member.date_of_birth = date.today()
        member.clean()   # não deve lançar

    def test_clean_data_nascimento_passada_nao_levanta_erro(self, member):
        member.date_of_birth = date(1990, 5, 15)
        member.clean()   # não deve lançar

    def test_clean_data_nascimento_nula_nao_levanta_erro(self, member):
        member.date_of_birth = None
        member.clean()   # não deve lançar


# ─────────────────────────────────────────────────────────────────────────────
# Member — slug
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberSlug:

    def test_slug_gerado_ao_criar(self, member):
        assert member.slug != ""
        assert member.slug is not None

    def test_slug_baseado_no_nome_completo(self, member):
        # "João Silva" → "joao-silva"
        assert "joao" in member.slug
        assert "silva" in member.slug

    def test_slug_unico_para_nomes_iguais(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        
        u1 = User.objects.create_user(email="a@teste.com", role="member")
        u2 = User.objects.create_user(email="b@teste.com", role="member")
        
        m1 = Member.objects.create(user=u1, first_name="Ana", last_name="Lima")
        m2 = Member.objects.create(user=u2, first_name="Ana", last_name="Lima")
        
        assert m1.slug != m2.slug
        assert m2.slug.startswith("ana-lima")

    def test_slug_incrementa_com_sufixo_numerico(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        
        base_data = dict(first_name="Pedro", last_name="Costa")
        
        u1 = User.objects.create_user(email="p1@teste.com", role="member")
        u2 = User.objects.create_user(email="p2@teste.com", role="member")
        u3 = User.objects.create_user(email="p3@teste.com", role="member")
        
        m1 = Member.objects.create(user=u1, **base_data)
        m2 = Member.objects.create(user=u2, **base_data)
        m3 = Member.objects.create(user=u3, **base_data)
        
        slugs = {m1.slug, m2.slug, m3.slug}
        assert len(slugs) == 3   

    def test_slug_usa_uuid_quando_nome_vazio(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(email="sem_nome@teste.com", role="member")
        member = Member.objects.create(user=user, first_name="", last_name="")
        expected_slug = f"membro-{member.id}"
        assert member.slug == expected_slug

    def test_slug_regenerado_ao_trocar_primeiro_nome(self, member):
        slug_original = member.slug
        member.first_name = "Carlos"
        member.save()
        member.refresh_from_db()
        assert member.slug != slug_original
        assert "carlos" in member.slug

    def test_slug_regenerado_ao_trocar_sobrenome(self, member):
        slug_original = member.slug
        member.last_name = "Ferreira"
        member.save()
        member.refresh_from_db()
        assert member.slug != slug_original

    def test_slug_regenerado_ao_trocar_username(self, member):
        slug_original = member.slug
        member.username = "joaosilva_oficial"
        member.save()
        member.refresh_from_db()
        assert member.slug == slug_original

    def test_slug_nao_alterado_sem_mudanca_de_nome(self, member):
        slug_original = member.slug
        member.phone = VALID_PHONE
        member.save()
        member.refresh_from_db()
        assert member.slug == slug_original


# ─────────────────────────────────────────────────────────────────────────────
# Member — has_name_changed
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberHasNameChanged:

    def test_falso_em_nova_instancia_nao_salva(self, db):
        from ecclesia.apps.users.models.member import Member
        from ecclesia.apps.users.models.user import User
        user = User.objects.create_user(email="novo@teste.com", role="member")
        member = Member(user=user, first_name="Novo", last_name="User")
        # _state.adding=True → nunca considera como alteração
        assert member.has_name_changed() is False

    def test_falso_quando_nome_nao_muda(self, member):
        member.first_name = "João"
        member.last_name = "Silva"
        member.username = "joaosilva"
        assert member.has_name_changed() is False

    def test_verdadeiro_quando_primeiro_nome_muda(self, member):
        member.first_name = "Carlos"
        assert member.has_name_changed() is True

    def test_verdadeiro_quando_sobrenome_muda(self, member):
        member.last_name = "Pereira"
        assert member.has_name_changed() is True

    def test_verdadeiro_quando_username_muda(self, member):
        member.username = "joaosilva_oficial"
        assert member.has_name_changed() is True


# ─────────────────────────────────────────────────────────────────────────────
# Member — phone
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberPhone:

    def test_normalize_phone_retorna_e164(self):
        from ecclesia.apps.users.models.member import Member
        resultado = Member.normalize_phone("+55 11 99999-8888")
        assert resultado == "+5511999998888"

    def test_normalize_phone_com_telefone_sem_formatacao(self):
        from ecclesia.apps.users.models.member import Member
        resultado = Member.normalize_phone("11999998888")
        assert resultado == "+5511999998888"

    def test_phone_pode_ser_definido_com_formato_internacional(self, member):
        member.phone = "+55 11 99999-8888"
        member.save()
        member.refresh_from_db()
        # O campo armazena no formato E.164
        assert str(member.phone) == "+5511999998888"


# ─────────────────────────────────────────────────────────────────────────────
# MemberAddress
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberAddress:

    def test_endereco_criado_com_sucesso(self, member):
        from ecclesia.apps.users.models.member import MemberAddress
        addr = MemberAddress.objects.create(
            member=member,
            **build_address_data()
        )
        assert addr.pk is not None

    def test_endereco_principal_por_padrao(self, member):
        from ecclesia.apps.users.models.member import MemberAddress
        addr = MemberAddress.objects.create(
            member=member,
            **build_address_data()
        )
        assert addr.principal is True

    def test_novo_endereco_principal_desativa_anterior(self, member):
        from ecclesia.apps.users.models.member import MemberAddress
        addr1 = MemberAddress.objects.create(
            member=member,
            **build_address_data(number="1")
        )
        addr2 = MemberAddress.objects.create(
            member=member,
            **build_address_data(number="2", principal=True)
        )
        addr1.refresh_from_db()
        assert addr1.principal is False
        assert addr2.principal is True

    def test_apenas_um_principal_por_member(self, member):
        from ecclesia.apps.users.models.member import MemberAddress
        for n in ("10", "20", "30"):
            MemberAddress.objects.create(
                member=member,
                **build_address_data(number=n)
            )
        total_principais = MemberAddress.objects.filter(
            member=member, principal=True
        ).count()
        assert total_principais == 1

    def test_str_retorna_endereco_formatado(self, member):
        from ecclesia.apps.users.models.member import MemberAddress
        addr = MemberAddress.objects.create(
            member=member,
            **build_address_data(
                road="Rua XV de Novembro",
                number="50",
                city="Curitiba",
                state="PR"
            )
        )
        assert str(addr) == "Rua XV de Novembro, 50 - Curitiba/PR"

    def test_slug_gerado_ao_criar(self, member):
        from ecclesia.apps.users.models.member import MemberAddress
        addr = MemberAddress.objects.create(
            member=member,
            **build_address_data()
        )
        assert addr.slug != ""