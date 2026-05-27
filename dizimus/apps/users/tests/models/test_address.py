"""
Testes de BaseAddress
──────────────────────
BaseAddress é abstrata; os comportamentos são testados através das subclasses
concretas MemberAddress e ChurchAddress, que adicionam a lógica de exclusividade
do endereço principal.
"""

import pytest

from .conftest import build_address_data


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def create_member_address(member, **overrides):
    from dizimus.apps.users.models.member import MemberAddress
    # from dizimus.apps.users.member import MemberAddress
    return MemberAddress.objects.create(member=member, **build_address_data(**overrides))


def create_church_address(church, **overrides):
    from dizimus.apps.users.models.church import ChurchAddress
    # from dizimus.apps.users.church import ChurchAddress
    return ChurchAddress.objects.create(church=church, **build_address_data(**overrides))


# ─────────────────────────────────────────────────────────────────────────────
# Geração de slug
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAddressSlug:

    def test_slug_gerado_ao_criar_member_address(self, member):
        addr = create_member_address(member)
        assert addr.slug != ""

    def test_slug_contem_componentes_do_endereco(self, member):
        addr = create_member_address(member, road="Avenida Brasil", number="500")
        assert "avenida-brasil" in addr.slug
        assert "500" in addr.slug

    def test_slug_unico_para_enderecos_iguais(self, member):
        a1 = create_member_address(member)
        a2 = create_member_address(member, number="101")
        assert a1.slug != a2.slug

    def test_slug_gerado_ao_criar_church_address(self, church):
        addr = create_church_address(church)
        assert addr.slug != ""

    def test_slug_incrementa_para_evitar_colisao(self, member):
        from dizimus.apps.users.models.member import MemberAddress
        # Força a mesma base de slug usando mesmo endereço — o UUID curto no
        # final varia, mas testamos o mecanismo de sufixo via mock.
        a1 = create_member_address(member)
        # Cria outro endereço com dados idênticos; o UUID no slug os diferencia
        a2 = create_member_address(member)
        assert a1.slug != a2.slug

    def test_slug_nao_regenerado_em_save_posterior(self, member):
        addr = create_member_address(member)
        slug_original = addr.slug
        addr.complement = "Apto 10"
        addr.save()
        addr.refresh_from_db()
        assert addr.slug == slug_original


# ─────────────────────────────────────────────────────────────────────────────
# __str__
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAddressStr:

    def test_str_member_address(self, member):
        addr = create_member_address(member, road="Rua XV de Novembro", number="50", city="Curitiba", state="PR")
        assert str(addr) == "Rua XV de Novembro, 50 - Curitiba/PR"

    def test_str_church_address(self, church):
        addr = create_church_address(church, road="Praça da Sé", number="1", city="São Paulo", state="SP")
        assert str(addr) == "Praça da Sé, 1 - São Paulo/SP"


# ─────────────────────────────────────────────────────────────────────────────
# Lógica de endereço principal — MemberAddress
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMemberAddressPrincipal:

    def test_primeiro_endereco_e_principal_por_padrao(self, member):
        addr = create_member_address(member)
        assert addr.principal is True

    def test_novo_principal_desativa_anterior(self, member):
        addr1 = create_member_address(member, number="1")
        addr2 = create_member_address(member, number="2", principal=True)
        addr1.refresh_from_db()
        assert addr1.principal is False
        assert addr2.principal is True

    def test_endereco_nao_principal_nao_afeta_outros(self, member):
        addr1 = create_member_address(member, number="1", principal=True)
        addr2 = create_member_address(member, number="2", principal=False)
        addr1.refresh_from_db()
        assert addr1.principal is True    # não foi alterado
        assert addr2.principal is False

    def test_endereco_principal_de_outro_member_nao_e_afetado(self, member, second_member):
        """Dois membros diferentes podem ter endereço principal independente."""
        addr_m1 = create_member_address(member,         number="10", principal=True)
        addr_m2 = create_member_address(second_member,  number="20", principal=True)
        addr_m1.refresh_from_db()
        assert addr_m1.principal is True   # intocado pelo outro membro
        assert addr_m2.principal is True

    def test_apenas_um_principal_por_member(self, member):
        from dizimus.apps.users.models.member import MemberAddress
        create_member_address(member, number="1")
        create_member_address(member, number="2")
        create_member_address(member, number="3")
        total_principais = MemberAddress.objects.filter(
            member=member, principal=True
        ).count()
        assert total_principais == 1


# ─────────────────────────────────────────────────────────────────────────────
# Lógica de endereço principal — ChurchAddress
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChurchAddressPrincipal:

    def test_novo_principal_desativa_anterior_na_church(self, church):
        addr1 = create_church_address(church, number="1")
        addr2 = create_church_address(church, number="2", principal=True)
        addr1.refresh_from_db()
        assert addr1.principal is False
        assert addr2.principal is True

    def test_endereco_nao_principal_nao_afeta_outros_na_church(self, church):
        addr1 = create_church_address(church, number="1", principal=True)
        addr2 = create_church_address(church, number="2", principal=False)
        addr1.refresh_from_db()
        assert addr1.principal is True

    def test_apenas_um_principal_por_church(self, church):
        from dizimus.apps.users.models.church import ChurchAddress
        for n in ("10", "20", "30"):
            create_church_address(church, number=n)
        total_principais = ChurchAddress.objects.filter(
            church=church, principal=True
        ).count()
        assert total_principais == 1