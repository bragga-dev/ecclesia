"""
Auth API — módulo de endpoints de autenticação.
"""
from ninja import Router

from .register import router as register_router
from .login import router as login_router
from .refresh import router as refresh_router
from .logout import router as logout_router
from .change_password import router as change_password_router
from .password_reset import router as password_reset_router

router = Router()

router.add_router("", register_router)
router.add_router("", login_router)
router.add_router("", refresh_router)
router.add_router("", logout_router)
router.add_router("", change_password_router)
router.add_router("", password_reset_router)

__all__ = ["router"]