# Re-exporta todos os símbolos públicos para manter compatibilidade retroativa.
# Código que fazia `from dizimus.apps.users.models import User` continua funcionando.

from .constants import ROLE_ADMIN, ROLE_MEMBER, ROLE_CHURCH
from .user_manager import UserManager
from .user import User, user_photo_path, DEFAULT_USER_PHOTO
from .base_address import BaseAddress
from .member import Member, MemberAddress, MemberChurch
from .church import Church, ChurchAddress, church_banner_path, DEFAULT_CHURCH_BANNER

__all__ = [
    # Constantes
    "ROLE_ADMIN",
    "ROLE_MEMBER",
    "ROLE_CHURCH",
    # Manager
    "UserManager",
    # User
    "User",
    "user_photo_path",
    "DEFAULT_USER_PHOTO",
    # Address base
    "BaseAddress",
    # Member
    "Member",
    "MemberAddress",
    "MemberChurch",
    # Church
    "Church",
    "ChurchAddress",
    "church_banner_path",
    "DEFAULT_CHURCH_BANNER",
]