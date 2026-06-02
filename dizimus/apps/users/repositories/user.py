"""
User Repository — persistência de User.
"""
from typing import Optional
from dizimus.apps.users.models.user import User


def create_user(
    *,
    email: str,
    password: str,
    role: str,
    phone: Optional[str] = None,
) -> User:
    phone_value = phone if phone is not None else ""
    user = User.objects.create_user(
        email=email,
        password=password,
        role=role,
        phone=phone_value,
    )
    return user


def update_user(user: User, **fields) -> User:
    for attr, value in fields.items():
        if value is not None:
            setattr(user, attr, value)
    user.save()
    return user


def activate_user(user: User) -> User:
    user.is_active = True
    user.is_trusty = True
    user.save(update_fields=["is_active", "is_trusty"])
    return user
