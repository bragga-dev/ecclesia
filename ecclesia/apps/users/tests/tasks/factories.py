# tests/factories.py
import factory
from django.contrib.auth.hashers import make_password
from ecclesia.apps.users.models.church import  Church
from ecclesia.apps.users.models.user import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.LazyFunction(lambda: make_password("test123"))
    role = User.UserRole.MEMBER
    is_active = True


class ChurchUserFactory(UserFactory):
    role = User.UserRole.CHURCH
    email = factory.Sequence(lambda n: f"church{n}@example.com")


class ChurchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Church
        django_get_or_create = ('full_name',)

    user = factory.SubFactory(ChurchUserFactory)
    full_name = factory.Sequence(lambda n: f"Igreja Teste {n}")
    phone = "+5511999998888"