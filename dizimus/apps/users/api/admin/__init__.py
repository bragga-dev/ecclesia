"""
Admin API — agrega todos os sub-routers do painel de administração.
"""
from ninja import Router

from .admin_churches import router as churches_router
from .admin_users import router as users_router
from .admin_members import router as members_router

router = Router()

router.add_router("/churches/", churches_router)
router.add_router("/users/", users_router)
router.add_router("/members/", members_router)