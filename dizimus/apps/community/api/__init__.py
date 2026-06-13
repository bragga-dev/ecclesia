# dizimus/apps/community/api/__init__.py
"""
Community API - módulo de endpoints.
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .member_church_router import router as member_church_router

router = Router(auth=JWTAuth())

router.add_router("", member_church_router)  