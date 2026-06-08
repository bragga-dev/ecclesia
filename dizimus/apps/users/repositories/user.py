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
    
) -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        role=role,
    )
    return user

def activate_user(user: User) -> User:
    user.is_active = True
    user.is_trusty = True
    user.save(update_fields=["is_active", "is_trusty"])
    return user
