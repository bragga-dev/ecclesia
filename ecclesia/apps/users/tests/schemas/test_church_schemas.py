# ecclesia/apps/users/tests/schemas/test_church_schemas.py

import pytest
from pydantic import ValidationError
from ecclesia.apps.users.schemas.church_schemas import (
    ChurchOut,
    ChurchUpdateIn,
    ChurchAddressIn,
    ChurchAddressOut,
    ChurchCreateIn,
    ChurchTypeEnum,
)


class TestChurchOut:
    """Testes do schema de saída da igreja"""

    def test_church_out_serialization(self, church_user):
        church = church_user.church
        data = ChurchOut.from_orm(church)
        
        assert data.id == church.id
        assert data.user.id == church_user.id
        assert data.is_verified == church.is_verified
        assert data.is_active == church_user.is_active
        assert data.cnpj == church.cnpj
        assert data.banner_url == church.banner_url
        assert data.church_type == church.church_type
        assert data.church_type_label == church.get_church_type_display()
        assert data.full_name == church.full_name

    def test_church_out_without_cnpj(self, church_user):
        church = church_user.church
        church.cnpj = None
        church.save()
        
        data = ChurchOut.from_orm(church)
        assert data.cnpj is None


class TestChurchCreateIn:
    """Testes do schema de criação de igreja"""

    def test_valid_create(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "full_name": "Igreja Nova",
            "cnpj": "12.345.678/0001-95",
            "church_type": ChurchTypeEnum.PARISH,
        }
        schema = ChurchCreateIn(**data)
        assert schema.full_name == "Igreja Nova"
        assert schema.church_type == ChurchTypeEnum.PARISH

    def test_valid_create_without_cnpj(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "full_name": "Igreja Comunitária",
        }
        schema = ChurchCreateIn(**data)
        assert schema.cnpj is None
        assert schema.church_type == ChurchTypeEnum.INDEPENDENT  

    def test_invalid_cnpj(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "full_name": "Igreja Inválida",
            "cnpj": "12.345.678/0001-96",
        }
        with pytest.raises(ValidationError) as exc_info:
            ChurchCreateIn(**data)
        assert "CNPJ inválido" in str(exc_info.value)

    def test_full_name_too_short(self):
        data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "full_name": "Ig",
        }
        with pytest.raises(ValidationError) as exc_info:
            ChurchCreateIn(**data)
        assert "String should have at least 3 characters" in str(exc_info.value)


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

    def test_cnpj_empty_string_is_valid(self):
        data = {"cnpj": ""}
        schema = ChurchUpdateIn(**data)
        assert schema.cnpj is None 

    def test_none_cnpj_is_valid(self):
        data = {"cnpj": None}
        schema = ChurchUpdateIn(**data)
        assert schema.cnpj is None

    def test_partial_update(self):
        data = {"instagram": "@igreja", "website": "https://igreja.com"}
        schema = ChurchUpdateIn(**data)
        assert schema.instagram == "@igreja"
        assert schema.website == "https://igreja.com"
        assert schema.cnpj is None

    def test_update_church_type(self):
        data = {"church_type": ChurchTypeEnum.COMMUNITY}
        schema = ChurchUpdateIn(**data)
        assert schema.church_type == ChurchTypeEnum.COMMUNITY

    def test_empty_update(self):
        schema = ChurchUpdateIn()
        assert schema.cnpj is None
        assert schema.instagram is None
        assert schema.website is None


class TestChurchAddressIn:
    """Testes do schema de endereço de igreja"""

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
        schema = ChurchAddressIn(**data)
        assert schema.cep == "01001-000"
        assert schema.road == "Praça da Sé"
        assert schema.state == "SP"

    def test_address_with_complement(self):
        data = {
            "cep": "01001-000",
            "road": "Praça da Sé",
            "number": "100",
            "district": "Sé",
            "city": "São Paulo",
            "state": "SP",
            "complement": "Sala 101",
            "principal": True
        }
        schema = ChurchAddressIn(**data)
        assert schema.complement == "Sala 101"

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
            ChurchAddressIn(**data)
        assert "Estado inválido" in str(exc_info.value)


class TestChurchAddressOut:
    """Testes do schema de saída de endereço de igreja"""

    def test_address_out_serialization(self, church_address):
        data = ChurchAddressOut.from_orm(church_address)
        
        assert data.id == church_address.id
        assert data.church_id == church_address.church_id
        assert data.cep == church_address.cep
        assert data.road == church_address.road
        assert data.number == church_address.number
        assert data.district == church_address.district
        assert data.city == church_address.city
        assert data.state == church_address.state
        assert data.country == church_address.country
        assert data.slug == church_address.slug