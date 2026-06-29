
from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.member import Member
from ecclesia.apps.users.models.church import Church
import uuid
from typing import Optional




def create_member_church(
    member: Member,
    church: Church,
    role: str = MemberChurch.Role.MEMBER,
    status: str = MemberChurch.Status.ACTIVE,
    contribution_type: str = MemberChurch.ContributionType.NONE,
) -> MemberChurch:
    return MemberChurch.objects.create(
        member=member,
        church=church,
        role=role,
        status=status,
        contribution_type=contribution_type,
    )


def update_member_church(member_church: MemberChurch, **fields) -> MemberChurch:
    for attr, value in fields.items():
        if value is not None:
            setattr(member_church, attr, value)
    member_church.full_clean()   
    member_church.save()
    return member_church


def delete_member_church_repository(membership: MemberChurch):
    membership.delete()