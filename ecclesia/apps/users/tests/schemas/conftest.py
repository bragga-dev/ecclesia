# ecclesia/apps/users/tests/schemas/conftest.py

import pytest
from datetime import date
from ecclesia.apps.users.models import User
from ecclesia.apps.users.models.member import Member
from ecclesia.apps.users.models.church import Church


@pytest.fixture
def member_user(db):
    """
    User com role='member' + perfil Member criado explicitamente.
    """
    user = User.objects.create_user(
        email="membro@teste.com",
        password="SenhaForte123!",
        role=User.UserRole.MEMBER,
        is_active=True,
    )
    Member.objects.create(
        user=user,
        username="membro_teste",
        first_name="João",
        last_name="Silva",
        cpf="529.982.247-25",
        date_of_birth=date(1990, 6, 15),
        phone="11999998888",
    )
    return user


@pytest.fixture
def church_user(db):
    """
    User com role='church' + perfil Church criado explicitamente.
    """
    user = User.objects.create_user(
        email="igreja@teste.com",
        password="SenhaForte123!",
        role=User.UserRole.CHURCH,
        is_active=True,
    )
    Church.objects.create(
        user=user,
        full_name="Igreja Teste",
        cnpj="11.222.333/0001-81",
        phone="1133334444",
    )
    return user


@pytest.fixture
def member_address(member_user):
    """Cria um endereço para o membro."""
    from ecclesia.apps.users.models.member import MemberAddress
    
    address = MemberAddress.objects.create(
        member=member_user.member,
        cep="01001-000",
        road="Praça da Sé",
        number="100",
        district="Sé",
        city="São Paulo",
        state="SP",
        country="Brasil",
        principal=True,
    )
    return address


@pytest.fixture
def church_address(church_user):
    """Cria um endereço para a igreja."""
    from ecclesia.apps.users.models.church import ChurchAddress
    
    address = ChurchAddress.objects.create(
        church=church_user.church,
        cep="02002-000",
        road="Avenida Paulista",
        number="1000",
        district="Bela Vista",
        city="São Paulo",
        state="SP",
        country="Brasil",
        principal=True,
    )
    return address