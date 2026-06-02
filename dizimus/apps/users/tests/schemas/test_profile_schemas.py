# dizimus/apps/users/tests/schemas/test_profile_schemas.py

import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from dizimus.apps.users.schemas.addresses_schemas import (
    ChurchUpdateIn,
    ChurchProfileOut,
    MemberUpdateIn,
    MemberProfileOut,
    AddressIn,
    AddressUpdateIn,
    AddressOut,
)


class TestChurchUpdateIn:
    """Testes do schema de atualização de igreja"""

    def test_valid_cnpj(self):
        data = {"cnpj": "12.345.678/0001-95"}
        schema = ChurchUpdateIn(**data)
        assert schema.cnpj == "12.345.678/0001-95"

    def test_invalid_cnpj(self):
        data = {"cnpj": "12.345.678/0001-96"}
        with pytest.raises(ValidationError) as exc_info:
            ChurchUpdateIn(**data)
        assert "CNPJ inválido" in str(exc_info.value)

    def test_partial_update(self):
        data = {"instagram": "@igreja", "website": "https://igreja.com"}
        schema = ChurchUpdateIn(**data)
        assert schema.instagram == "@igreja"
        assert schema.website == "https://igreja.com"
        assert schema.cnpj is None

    def test_about_exceeds_max_length(self):
        long_text = "A" * 1001
        data = {"about": long_text}
        with pytest.raises(ValidationError) as exc_info:
            ChurchUpdateIn(**data)
        assert "1000 caracteres" in str(exc_info.value)

    def test_valid_about_length(self):
        data = {"about": "Descrição da igreja com menos de 1000 caracteres."}
        schema = ChurchUpdateIn(**data)
        assert len(schema.about) < 1000

    def test_empty_update(self):
        schema = ChurchUpdateIn()
        assert schema.cnpj is None
        assert schema.instagram is None
        assert schema.website is None


class TestChurchProfileOut:
    """Testes do schema de saída do perfil da igreja"""

    def test_church_profile_output(self, church_user):
        church = church_user.church
        data = ChurchProfileOut.from_orm(church)
        assert data.cnpj == church.cnpj
        assert data.total_members == church.total_members
        assert data.is_verified == church.is_verified
        assert data.banner_url == church.banner_url


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
        today = date.today()
        data = {"date_of_birth": today.replace(year=today.year - 20)}
        schema = MemberUpdateIn(**data)
        assert schema.date_of_birth is not None

    def test_future_date_of_birth(self):
        future_date = date.today() + timedelta(days=1)
        data = {"date_of_birth": future_date}
        with pytest.raises(ValidationError) as exc_info:
            MemberUpdateIn(**data)
        assert "futuro" in str(exc_info.value).lower()

    def test_partial_update(self):
        data = {"cpf": "529.982.247-25"}
        schema = MemberUpdateIn(**data)
        assert schema.cpf == "529.982.247-25"
        assert schema.date_of_birth is None


class TestMemberProfileOut:
    """Testes do schema de saída do perfil do membro"""

    def test_member_profile_output(self, member_user):
        member = member_user.member
        data = MemberProfileOut.from_orm(member)
        assert data.cpf == member.cpf
        assert data.date_of_birth == member.date_of_birth


class TestAddressIn:
    """Testes do schema de endereço"""

    def test_valid_address(self):
        data = {
            "cep": "01001-000",
            "road": "Praça da Sé",
            "number": "100",
            "district": "Sé",
            "city": "São Paulo",
            "state": "SP",
            "principal": True
        }
        schema = AddressIn(**data)
        assert schema.cep == "01001-000"
        assert schema.state == "SP"

    def test_invalid_state(self):
        data = {
            "cep": "01001-000",
            "road": "Praça da Sé",
            "number": "100",
            "district": "Sé",
            "city": "São Paulo",
            "state": "XX",
        }
        with pytest.raises(ValidationError) as exc_info:
            AddressIn(**data)
        assert "Estado inválido" in str(exc_info.value)


class TestAddressUpdateIn:
    """Testes do schema de atualização de endereço"""

    def test_partial_update(self):
        data = {"road": "Avenida Paulista", "number": "1000"}
        schema = AddressUpdateIn(**data)
        assert schema.road == "Avenida Paulista"
        assert schema.number == "1000"
        assert schema.cep is None
        assert schema.state is None

    def test_update_state(self):
        data = {"state": "RJ"}
        schema = AddressUpdateIn(**data)
        assert schema.state == "RJ"

    def test_invalid_state_in_update(self):
        data = {"state": "XX"}
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateIn(**data)
        assert "Estado inválido" in str(exc_info.value)

    def test_empty_update(self):
        schema = AddressUpdateIn()
        assert all(v is None for v in schema.dict().values())


class TestAddressOut:
    """Testes do schema de saída de endereço"""

    def test_address_output(self, member_user):
        from dizimus.apps.users.models import MemberAddress
        address = MemberAddress.objects.filter(member=member_user.member).first()
        if address:
            data = AddressOut.from_orm(address)
            assert data.id == address.id
            assert data.cep == address.cep
            assert data.slug == address.slug