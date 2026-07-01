# Re-exporta todos os símbolos públicos para manter compatibilidade retroativa
from .constants import ROLE_ADMIN, ROLE_MEMBER, ROLE_CHURCH
from ecclesia.apps.users.models.user_manage import UserManager
from .user import User, user_photo_path, DEFAULT_USER_PHOTO
from .base_address import BaseAddress
from .member import Member, MemberAddress
from .church import Church, ChurchAddress, church_banner_path, DEFAULT_CHURCH_BANNER
from .audit_user_model import AuditLog
from ecclesia.apps.users.models.system_permission import SystemPermission  
from ecclesia.apps.users.models.member_church_permission import MemberChurchPermission  
from ecclesia.apps.community.models.member_church_model import MemberChurch  

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
    "AuditLog",
    # Address base
    "BaseAddress",
    # Member
    "Member",
    "MemberAddress",
    # Church
    "Church",
    "ChurchAddress",
    "church_banner_path",
    "DEFAULT_CHURCH_BANNER",
    # MemberChurch
    "MemberChurch",  
    # Permissions )
    "SystemPermission",
    "MemberChurchPermission",  
]