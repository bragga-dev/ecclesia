

import pytest


@pytest.fixture
def member_church_link(db, member, church):
    """Cria um vínculo MemberChurch com status PENDING (padrão)."""
    from ecclesia.apps.community.models.member_church_model import MemberChurch
    return MemberChurch.objects.create(member=member, church=church)