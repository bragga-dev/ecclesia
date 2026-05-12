from django.db import transaction

from users.models import User
from churches.models import Church


@transaction.atomic
def create_church_user(
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    church_name: str,
    cnpj: str = None,
):
    """
    Cria um usuário igreja e sua igreja.
    """

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role="church",
    )

    church = Church.objects.create(
        user=user,
        name=church_name,
        cnpj=cnpj,
    )

    return church