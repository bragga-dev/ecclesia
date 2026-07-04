# ecclesia/apps/community/api/member_church_router/__init__.py
from .member_church_router import router
from .member_permission_router import router as member_permission_router    

__all__ = ['router', 'member_permission_router']