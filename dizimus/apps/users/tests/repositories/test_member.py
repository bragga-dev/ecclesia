# dizimus/apps/users/tests/repositories/test_member.py

import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from dizimus.apps.users.repositories.member import (
    create_member_profile,
    update_member_profile
)
from dizimus.apps.users.models import Member


@pytest.mark.django_db
class TestMemberRepository:
    """Testes do repositório de Member"""

    def test_create_member_profile_success(self, user_factory):
        """Deve criar perfil de membro com sucesso"""
        user = user_factory(role="member")

        member = create_member_profile(user)

        assert member.id is not None
        assert member.user == user
        assert member.cpf is None
        assert member.date_of_birth is None

    def test_create_member_profile_with_fields(self, user_factory):
        """Deve criar perfil de membro com campos opcionais"""
        user = user_factory(role="member")
        birth_date = date(1990, 5, 15)

        member = create_member_profile(
            user,
            first_name="João",
            last_name="Silva",
            username="joaosilva",
            cpf="529.982.247-25",
            date_of_birth=birth_date
        )

        assert member.first_name == "João"
        assert member.last_name == "Silva"
        assert member.username == "joaosilva"
        assert member.cpf == "529.982.247-25"
        assert member.date_of_birth == birth_date

    def test_create_member_profile_only_once_per_user(self, user_factory):
        """Deve permitir apenas um perfil de membro por usuário"""
        user = user_factory(role="member")

        member1 = create_member_profile(user)
        member2 = Member.objects.filter(user=user).first()

        assert member1.id == member2.id
        assert Member.objects.filter(user=user).count() == 1

    def test_update_member_profile_success(self, member_user):
        """Deve atualizar perfil do membro"""
        member = member_user.member
        birth_date = date(1990, 5, 15)

        updated_member = update_member_profile(
            member,
            cpf="529.982.247-25",
            date_of_birth=birth_date
        )

        assert updated_member.cpf == "529.982.247-25"
        assert updated_member.date_of_birth == birth_date

    def test_update_member_profile_partial(self, member_user):
        """Deve atualizar apenas campos fornecidos"""
        member = member_user.member
        original_cpf = member.cpf

        updated_member = update_member_profile(
            member,
            date_of_birth=date(1995, 3, 20)
        )

        assert updated_member.date_of_birth == date(1995, 3, 20)
        assert updated_member.cpf == original_cpf

    def test_update_member_profile_with_none_values(self, member_user):
        """Deve ignorar campos com valor None"""
        member = member_user.member
        original_cpf = member.cpf

        updated_member = update_member_profile(
            member,
            cpf=None,
            first_name="NovoNome"
        )

        assert updated_member.cpf == original_cpf
        assert updated_member.first_name == "NovoNome"

    def test_update_member_profile_with_invalid_cpf_raises_error(self, member_user):
        """Deve lançar erro ao tentar atualizar com CPF inválido"""
        member = member_user.member

        with pytest.raises(ValidationError):
            update_member_profile(member, cpf="111.111.111-11")

    def test_update_member_profile_with_future_birth_date_raises_error(self, member_user):
        """Deve lançar erro ao tentar atualizar com data de nascimento futura"""
        member = member_user.member
        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValidationError):
            update_member_profile(member, date_of_birth=future_date)

    def test_update_member_profile_cleans_data(self, member_user):
        """Deve chamar full_clean() antes de salvar"""
        member = member_user.member

        # Isso deve disparar validação
        with pytest.raises(ValidationError):
            update_member_profile(member, date_of_birth=date.today() + timedelta(days=30))