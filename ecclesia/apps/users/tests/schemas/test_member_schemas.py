# ecclesia/apps/users/tests/schemas/test_member_schemas.py

import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from ecclesia.apps.users.schemas.member_schemas import (
    MemberOut,
    MemberCreateIn,
    MemberUpdateIn,
    MemberAddressIn,
    MemberAddressOut,
    MemberAddressUpdateIn,
)


class TestMemberOut:
    """Testes do schema de saída do membro"""

    def test_member_out_serialization(self, member_user):
        member = member_user.member
        data = MemberOut.from_orm(member)
        
        assert data.id == member.id
        assert data.user.id == member_user.id
        assert data.username == member.username
        assert data.first_name == member.first_name
        assert data.last_name == member.last_name
        assert data.cpf == member.cpf
        assert data.phone == str(member.phone)
        assert data.date_of_birth == member.date_of_birth

    def test_member_out_without_phone(self, member_user):
        member = member_user.member
        member.phone = ""
        member.save()
        
        data = MemberOut.from_orm(member)
        assert data.phone is None


class TestMemberCreateIn:
    """Testes do schema de criação de membro"""

    def test_valid_create(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "joaosilva",
            "first_name": "João",
            "last_name": "Silva",
            "cpf": "529.982.247-25",
            "phone": "11999998888",
            "date_of_birth": date(1990, 6, 15),
        }
        schema = MemberCreateIn(**data)
        assert schema.username == "joaosilva"
        assert schema.first_name == "João"
        assert schema.last_name == "Silva"

    def test_valid_create_without_cpf(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "joaosilva",
            "first_name": "João",
            "last_name": "Silva",
        }
        schema = MemberCreateIn(**data)
        assert schema.cpf is None

    def test_invalid_cpf(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "joaosilva",
            "first_name": "João",
            "last_name": "Silva",
            "cpf": "111.111.111-11",
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberCreateIn(**data)
        assert "CPF inválido" in str(exc_info.value)

    def test_future_date_of_birth(self):
        future_date = date.today() + timedelta(days=1)
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "joaosilva",
            "first_name": "João",
            "last_name": "Silva",
            "date_of_birth": future_date,
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberCreateIn(**data)
        assert "futuro" in str(exc_info.value).lower()

    def test_username_with_invalid_characters(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "joao@silva!",
            "first_name": "João",
            "last_name": "Silva",
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberCreateIn(**data)
        assert "Username inválido" in str(exc_info.value)

    def test_username_too_short(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "jo",
            "first_name": "João",
            "last_name": "Silva",
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberCreateIn(**data)
        assert "String should have at least 3 characters" in str(exc_info.value)


class TestMemberUpdateIn:
    """Testes do schema de atualização de membro"""

    def test_valid_cpf(self):
        data = {"cpf": "529.982.247-25"}
        schema = MemberUpdateIn(**data)
        assert schema.cpf == "529.982.247-25"

    def test_invalid_cpf(self):
        data = {"cpf": "111.111.111-11"}
        with pytest.raises(ValidationError) as exc_info:
            MemberUpdateIn(**data)
        assert "CPF inválido" in str(exc_info.value)

    def test_valid_date_of_birth(self):
        data = {"date_of_birth": date(1990, 1, 1)}
        schema = MemberUpdateIn(**data)
        assert schema.date_of_birth == date(1990, 1, 1)

    def test_future_date_of_birth(self):
        future_date = date.today() + timedelta(days=1)
        data = {"date_of_birth": future_date}
        with pytest.raises(ValidationError) as exc_info:
            MemberUpdateIn(**data)
        assert "futuro" in str(exc_info.value).lower()

    def test_partial_update(self):
        data = {"cpf": "529.982.247-25", "first_name": "Carlos"}
        schema = MemberUpdateIn(**data)
        assert schema.cpf == "529.982.247-25"
        assert schema.first_name == "Carlos"
        assert schema.last_name is None

    def test_empty_update(self):
        schema = MemberUpdateIn()
        assert all(v is None for v in schema.dict().values())


class TestMemberAddressIn:
    """Testes do schema de endereço de membro"""

    def test_valid_address(self):
        data = {
            "cep": "01001-000",
            "road": "Praça da Sé",
            "number": "100",
            "district": "Sé",
            "city": "São Paulo",
            "state": "SP",
            "complement": "Apto 101",
            "principal": True
        }
        schema = MemberAddressIn(**data)
        assert schema.cep == "01001-000"
        assert schema.complement == "Apto 101"

    def test_invalid_state(self):
        data = {
            "cep": "01001-000",
            "road": "Praça da Sé",
            "number": "100",
            "district": "Sé",
            "city": "São Paulo",
            "state": "XX",
            "principal": True
        }
        with pytest.raises(ValidationError) as exc_info:
            MemberAddressIn(**data)
        assert "Estado inválido" in str(exc_info.value)


class TestMemberAddressOut:
    """Testes do schema de saída de endereço de membro"""

    def test_address_out_serialization(self, member_address):
        data = MemberAddressOut.from_orm(member_address)
        
        assert data.id == member_address.id
        assert data.member_id == member_address.member_id
        assert data.cep == member_address.cep
        assert data.road == member_address.road
        assert data.number == member_address.number
        assert data.district == member_address.district
        assert data.city == member_address.city
        assert data.state == member_address.state
        assert data.country == member_address.country
        assert data.slug == member_address.slug


class TestMemberAddressUpdateIn:
    """Testes do schema de atualização de endereço de membro"""

    def test_partial_update(self):
        data = {"road": "Avenida Paulista", "number": "1000"}
        schema = MemberAddressUpdateIn(**data)
        assert schema.road == "Avenida Paulista"
        assert schema.number == "1000"
        assert schema.cep is None

    def test_invalid_state_in_update(self):
        data = {"state": "XX"}
        with pytest.raises(ValidationError) as exc_info:
            MemberAddressUpdateIn(**data)
        assert "Estado inválido" in str(exc_info.value)