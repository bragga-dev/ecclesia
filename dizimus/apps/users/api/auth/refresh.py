"""
Refresh endpoint — renovação de access token.
"""
from ninja import Router
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    RefreshIn,
    MessageOut,
)
from dizimus.apps.users.exceptions import InvalidToken

router = Router()


@router.post(
    "/refresh",
    response={200: dict, 401: MessageOut},
    auth=None,
    summary="Renovar access token",
)
def refresh(request, payload: RefreshIn):
    try:
        data = services.refresh_access_token(payload.refresh)
        return 200, data
    except InvalidToken as e:
        return 401, {"detail": str(e)}