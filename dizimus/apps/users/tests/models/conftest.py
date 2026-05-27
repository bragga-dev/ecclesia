"""
conftest.py — fixtures globais para os testes dos models de users.

Estratégia de isolamento
─────────────────────────
• Os validators de imagem (validate_image_file) e de CEP (validar_cep) são
  desativados no nível dos campos (field.validators = []) para que os testes
  não dependam de arquivos reais no bucket nem de consulta a webservices.
  Ambos os fixtures têm scope="session" e são restaurados ao final.

• CPF, CNPJ e telefone usam valores reais e válidos para manter os testes dos
  próprios validators significativos.

• Todos os fixtures de banco têm scope="function" (padrão) para garantir
  isolamento entre testes.
"""

import pytest
from django.utils import timezone

# ─── Documentos / contatos válidos para uso nos testes ───────────────────────
VALID_CPF   = "529.982.247-25"
INVALID_CPF = "111.111.111-11"          # dígitos todos iguais → inválido

VALID_CNPJ   = "11.222.333/0001-81"
INVALID_CNPJ = "00.000.000/0000-00"

VALID_CEP = "01310-100"
VALID_PHONE = "+55 11 99999-8888"


# ─── Patches de session ───────────────────────────────────────────────────────

@pytest.fixture(autouse=True, scope="session")
def disable_image_validators():
    """
    Remove validate_image_file das listas de validators dos campos ImageField.
    Esses validators tentam ler o arquivo (extensão / tamanho), o que falha
    em testes que não sobem o MinIO.
    """
    # from dizimus.apps.users.user import User
    # from dizimus.apps.users.church import Church


    from dizimus.apps.users.models.user import User
    from dizimus.apps.users.models.church import  Church

    photo_field  = User._meta.get_field("photo")
    banner_field = Church._meta.get_field("banner")

    orig_photo  = photo_field.validators[:]
    orig_banner = banner_field.validators[:]

    photo_field.validators  = []
    banner_field.validators = []

    yield

    photo_field.validators  = orig_photo
    banner_field.validators = orig_banner


@pytest.fixture(autouse=True, scope="session")
def disable_cep_validators():
    """
    Remove validar_cep das listas de validators dos campos CEP.
    Isso evita chamadas a webservices de validação durante os testes.
    """
    from dizimus.apps.users.models.member import MemberAddress
    from dizimus.apps.users.models.church import ChurchAddress

    originals = {}
    for cls in (MemberAddress, ChurchAddress):
        field = cls._meta.get_field("cep")
        originals[cls] = field.validators[:]
        field.validators = []

    yield

    for cls, orig in originals.items():
        cls._meta.get_field("cep").validators = orig


# ─── Builders de dados ────────────────────────────────────────────────────────

def build_user_data(**overrides):
    """Retorna dict mínimo para criar um User (MEMBER) válido."""
    data = {
        "email":      "usuario@teste.com",
        "username":   "usuario",
        "first_name": "João",
        "last_name":  "Silva",
        "password":   "SenhaForte123!",
    }
    data.update(overrides)
    return data


def build_address_data(**overrides):
    """Retorna dict mínimo para criar um endereço válido."""
    data = {
        "cep":      VALID_CEP,
        "road":     "Rua das Flores",
        "number":   "100",
        "district": "Centro",
        "city":     "São Paulo",
        "state":    "SP",
    }
    data.update(overrides)
    return data


# ─── Fixtures de usuários ─────────────────────────────────────────────────────

@pytest.fixture
def member_user(db):
    from dizimus.apps.users.models.user import User
    return User.objects.create_user(**build_user_data())


@pytest.fixture
def church_user(db):
    from dizimus.apps.users.models import User
    return User.objects.create_user(**build_user_data(
        email="igreja@teste.com",
        username="igrejateste",
        first_name="Igreja",
        last_name="Batista",
        role="church",
    ))


@pytest.fixture
def admin_user(db):
    from dizimus.apps.users.models.user import User
    return User.objects.create_superuser(**build_user_data(
        email="admin@teste.com",
        username="adminroot",
        first_name="Admin",
        last_name="Root",
    ))


@pytest.fixture
def second_member_user(db):
    from dizimus.apps.users.models.user import User
    return User.objects.create_user(**build_user_data(
        email="outro@teste.com",
        username="outrousuario",
        first_name="Maria",
        last_name="Souza",
    ))


# ─── Fixtures de entidades de negócio ─────────────────────────────────────────

@pytest.fixture
def member(db, member_user):
    from dizimus.apps.users.models.member import Member
    return Member.objects.create(user=member_user)


@pytest.fixture
def second_member(db, second_member_user):
    from dizimus.apps.users.models.member import Member
    return Member.objects.create(user=second_member_user)


@pytest.fixture
def church(db, church_user):
    from dizimus.apps.users.models.church import Church
    return Church.objects.create(user=church_user)



# Fixtures de relacionamento entre entidades (ex: MemberChurch) podem ser importados
# dos testes de community, já que dependem do mesmo modelo e não têm relação com
@pytest.fixture
def member_church_link(db, member, church):
    """Cria um vínculo MemberChurch com status PENDING (padrão)."""
    from dizimus.apps.community.models.member_church import MemberChurch
    return MemberChurch.objects.create(member=member, church=church)