# ecclesia/apps/community/api/__init__.py
"""
Community API - módulo de endpoints.
"""
from ninja import Router
from ecclesia.apps.users.permissions import ChurchOnlyAuth
from .member_church_router import router as member_church_router
from .church_in_church_router import router as church_in_church_router
from .member_church_router.member_permission_router import router as member_permission_router   

router = Router(auth=ChurchOnlyAuth())

router.add_router("", member_church_router, tags=["Church Members"])
router.add_router("", church_in_church_router, tags=["Church in Church"])
router.add_router("", member_permission_router, tags=["Member Permissions"])
