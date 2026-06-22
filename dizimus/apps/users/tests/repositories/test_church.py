# dizimus/apps/users/tests/repositories/test_church.py

import pytest
from dizimus.apps.users.repositories.church import (
    create_church_profile,
    update_church_profile,
    set_church_as_verified,
    set_church_as_unverified,
)
from dizimus.apps.users.models import Church


@pytest.mark.django_db
class TestChurchRepository:
    """Testes do repositório de Church"""

    def test_create_church_profile_success(self, user_factory):
        """Deve criar perfil de igreja com sucesso"""
        user = user_factory(role="church")

        church = create_church_profile(user)

        assert church.id is not None
        assert church.user == user
        assert church.is_verified is False

    def test_create_church_profile_with_fields(self, user_factory):
        """Deve criar perfil de igreja com campos opcionais"""
        user = user_factory(role="church")

        church = create_church_profile(
            user,
            full_name="Igreja Amor",
            cnpj="15.304.858/0001-17",
            instagram="https://instagram.com/igrejaamor", 
            website="https://igrejaamor.com",
            about="Uma igreja acolhedora"
        )

        assert church.full_name == "Igreja Amor"
        assert church.cnpj == "15.304.858/0001-17"
        assert church.instagram == "https://instagram.com/igrejaamor"
        assert church.website == "https://igrejaamor.com"
        assert church.about == "Uma igreja acolhedora"

    def test_create_church_profile_only_once_per_user(self, user_factory):
        """Deve permitir apenas um perfil de igreja por usuário"""
        user = user_factory(role="church")

        church1 = create_church_profile(user)
        church2 = Church.objects.filter(user=user).first()

        assert church1.id == church2.id
        assert Church.objects.filter(user=user).count() == 1

    def test_update_church_profile_success(self, church_user):
        """Deve atualizar perfil da igreja"""
        church = church_user.church

        updated_church = update_church_profile(
            church,
            cnpj="19.895.017/0001-82",
            instagram="https://instagram.com/igrejaamor",  
            website="https://igrejaamor.com",
            about="Uma igreja cheia de amor"
        )

        assert updated_church.cnpj == "19.895.017/0001-82"
        assert updated_church.instagram == "https://instagram.com/igrejaamor"
        assert updated_church.website == "https://igrejaamor.com"
        assert updated_church.about == "Uma igreja cheia de amor"

    def test_update_church_profile_partial(self, church_user):
        """Deve atualizar apenas campos fornecidos"""
        church = church_user.church
        original_cnpj = church.cnpj

        updated_church = update_church_profile(
            church,
            instagram="https://instagram.com/novaigreja" 
        )

        assert updated_church.instagram == "https://instagram.com/novaigreja"
        assert updated_church.cnpj == original_cnpj

    def test_update_church_profile_with_none_values(self, church_user):
        """Deve ignorar campos com valor None"""
        church = church_user.church
        original_cnpj = church.cnpj

        updated_church = update_church_profile(
            church,
            cnpj=None,
            instagram="https://instagram.com/teste"  
        )

        assert updated_church.cnpj == original_cnpj
        assert updated_church.instagram == "https://instagram.com/teste"

    def test_set_church_as_verified(self, church_user):
        """Deve marcar igreja como verificada"""
        church = church_user.church
        assert church.is_verified is False

        verified_church = set_church_as_verified(church)

        assert verified_church.is_verified is True

    def test_set_church_as_verified_already_verified(self, church_user):
        """Marcar igreja já verificada não deve causar erro"""
        church = church_user.church
        set_church_as_verified(church)
        set_church_as_verified(church)

        assert church.is_verified is True

    def test_set_church_as_unverified(self, church_user):
        """Deve marcar igreja como não verificada"""
        church = church_user.church
        set_church_as_verified(church)
        assert church.is_verified is True
        unverified_church = set_church_as_unverified(church)
        assert unverified_church.is_verified is False

    def test_set_church_as_unverified_already_unverified(self, church_user):
        """Marcar igreja já não verificada não deve causar erro"""
        church = church_user.church
        assert church.is_verified is False

        set_church_as_unverified(church)

        assert church.is_verified is False

    def test_update_church_profile_returns_church_instance(self, church_user):
        """Deve retornar a instância da igreja atualizada"""
        church = church_user.church
        result = update_church_profile(
            church,
            instagram="https://instagram.com/teste"  
        )

        assert isinstance(result, Church)
        assert result == church