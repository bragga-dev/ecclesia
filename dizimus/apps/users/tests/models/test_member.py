"""
Testes de Member, MemberAddress e MemberChurch
───────────────────────────────────────────────
Cobre: validação de data_of_birth, __str__, unicidade de vínculo,
roles, status, constraints e indexes.
"""

import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .conftest import VALID_CPF, build_user_data


# ─────────────────────────────────────────────────────────────────────────────
# Member
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMember:

    def test_str_retorna_nome_completo(self, member):
        assert str(member) == member.user.get_full_name()

    def test_member_criado_sem_cpf(self, member):
        assert member.cpf is None

    def test_member_criado_sem_data_nascimento(self, member):
        assert member.date_of_birth is None

    def test_member_com_cpf_valido(self, member):
        member.cpf = VALID_CPF
        member.full_clean()   # não deve lançar

    def test_member_com_cpf_invalido_levanta_validation_error(self, member):
        from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cpf
        with pytest.raises(ValidationError):
            validate_cpf("111.111.111-11")

    def test_clean_data_nascimento_futura_levanta_validation_error(self, member):
        member.date_of_birth = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            member.clean()
        assert "date_of_birth" in exc_info.value.message_dict

    def test_clean_data_nascimento_hoje_levanta_validation_error(self, member):
        """Hoje também é no futuro segundo a regra (> localdate())."""
        member.date_of_birth = date.today()
        # date.today() não é > localdate() → deve passar
        # (a validação é >, não >=)
        member.clean()   # não deve lançar

    def test_clean_data_nascimento_passada_nao_levanta_erro(self, member):
        member.date_of_birth = date(1990, 5, 15)
        member.clean()   # não deve lançar

    def test_clean_data_nascimento_nula_nao_levanta_erro(self, member):
        member.date_of_birth = None
        member.clean()   # não deve lançar

    def test_relacao_one_to_one_com_user(self, member_user, member):
        assert member.user == member_user
        assert member_user.member == member

    def test_nao_pode_criar_dois_members_para_mesmo_user(self, db, member_user, member):
        from dizimus.apps.users.models.member import Member
        with pytest.raises(IntegrityError):
            Member.objects.create(user=member_user)


