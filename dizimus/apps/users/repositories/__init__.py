"""
Repositories — escrita no banco.
Toda persistência passa por aqui.
"""
from .user import (
    create_user,
    update_user,
    activate_user,
)
from .photo import (
    set_user_photo,
    remove_user_photo,
    set_church_banner,
    remove_church_banner,
)
from .church import (
    create_church_profile,
    update_church_profile,
)
from .member import (
    create_member_profile,
    update_member_profile,
)
from .address import (
    # Church addresses
    
    create_church_address,
    update_church_address,
    delete_church_address,
    # Member addresses
    
    create_member_address,
    update_member_address,
    delete_member_address,
)

__all__ = [
    # User
    "create_user",
    "update_user",
    "activate_user",
    # Photo
    "set_user_photo",
    "remove_user_photo",
    "set_church_banner",
    "remove_church_banner",
    # Church
    "create_church_profile",
    "update_church_profile",
    # Member
    "create_member_profile",
    "update_member_profile",
    # Address - Church
    "create_church_address",
    "update_church_address",
    "delete_church_address",
    # Address - Member
    "create_member_address",
    "update_member_address",
    "delete_member_address",
]
