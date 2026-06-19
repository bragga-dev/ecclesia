# dizimus/apps/users/tests/schemas/test_profile_schemas.py

import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from dizimus.apps.users.schemas.profile_church_schema import ChurchProfileOut
from dizimus.apps.users.schemas.profile_member_schema import MemberProfileOut
from dizimus.apps.users.schemas.users_schemas import UserRoleEnum


class TestChurchProfileOut:
    """Testes do schema de saída do perfil da igreja"""

    def test_church_profile_output(self, church_user):
        user = church_user
        church = user.church
        
        data = ChurchProfileOut.from_orm(user, church)
        
        # User fields
        assert data.id == user.id
        assert data.email == user.email
        assert data.photo_url == user.photo_url
        assert data.role == user.role
        assert data.role_label == user.get_role_display()
        
        # Church fields
        assert data.full_name == church.full_name
        assert data.cnpj == church.cnpj
        assert data.instagram == church.instagram
        assert data.website == church.website
        assert data.about == church.about
        assert data.phone == str(church.phone)
        assert data.slug == church.slug
        assert data.church_type_label == church.get_church_type_display()
        assert data.church_type == church.church_type
        assert data.total_members == church.total_members
        assert data.is_verified == church.is_verified
        assert data.banner_url == church.banner_url

    def test_church_profile_without_optional_fields(self, church_user):
        user = church_user
        church = user.church
        church.instagram = None
        church.website = None
        church.about = None
        church.phone = ""
        church.save()
        
        data = ChurchProfileOut.from_orm(user, church)
        
        assert data.instagram is None
        assert data.website is None
        assert data.about is None
        assert data.phone is None
  


class TestMemberProfileOut:
    """Testes do schema de saída do perfil do membro"""

    def test_member_profile_output(self, member_user):
        user = member_user
        member = user.member
        
        data = MemberProfileOut.from_orm(user, member)
        
        # User fields
        assert data.id == user.id
        assert data.email == user.email
        assert data.photo_url == user.photo_url
        assert data.role == user.role
        assert data.role_label == user.get_role_display()
        
        # Member fields
        assert data.username == member.username
        assert data.first_name == member.first_name
        assert data.last_name == member.last_name
        assert data.slug == member.slug
        assert data.cpf == member.cpf
        assert data.phone == str(member.phone)
        assert data.date_of_birth == member.date_of_birth

    def test_member_profile_without_optional_fields(self, member_user):
        user = member_user
        member = user.member
        member.phone = ""
        member.cpf = None
        member.save()
        
        data = MemberProfileOut.from_orm(user, member)
        
        assert data.phone is None
        assert data.cpf is None