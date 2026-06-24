# dizimus/apps/community/api/__init__.py
"""
Community API - módulo de endpoints.
"""
from ninja import Router
from dizimus.apps.users.permissions import ChurchOnlyAuth
from .member_church_router import router as member_church_router
from .church_in_church_router import router as church_in_church_router

router = Router(auth=ChurchOnlyAuth())

router.add_router("", member_church_router, tags=["Church Members"])
router.add_router("", church_in_church_router, tags=["Church in Church"])