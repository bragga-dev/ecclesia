"""
Users API - módulo de endpoints.
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .verification import router as verification_router
from dizimus.apps.users.api.me import router as me_router
from .profiles import router as profiles_router
from .addresses import router as addresses_router


router = Router(auth=JWTAuth())

router.add_router("", me_router)             # /me, /me/photo
router.add_router("", profiles_router)       # /me/profile, /me/banner
router.add_router("", addresses_router)      # /me/addresses
router.add_router("", verification_router)   # /verify-email, /resend-verification
