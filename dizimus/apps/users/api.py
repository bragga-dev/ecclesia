from ninja import Router

from users.services import (
    create_church_user
)

router = Router()


@router.post("/churches")
def create_church(request, payload):

    church = create_church_user(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        church_name=payload.church_name,
        cnpj=payload.cnpj,
    )

    return {
        "id": church.id
    }