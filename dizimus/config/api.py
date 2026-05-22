from ninja import NinjaAPI, Swagger
from ninja_jwt.authentication import JWTAuth
from ninja.errors import ValidationError, AuthenticationError
from django.http import HttpRequest
from django.http import JsonResponse

# USERS
from dizimus.apps.users.api.auth import router as auth_router
from dizimus.apps.users.api import router as users_router

# CHURCHES
# ajuste o import conforme a estrutura real
# from dizimus.apps.churches.api import router as churches_router

# MEMBERS
# ajuste o import conforme a estrutura real
# from dizimus.apps.members.api import router as members_router


api = NinjaAPI(
    title="DIZIMUS API",
    version="1.0.0",
    description="API para gerenciamento de dízimos.",
    auth=JWTAuth(),
    urls_namespace="api",
    docs=Swagger(settings={
        "persistAuthorization": True,
    })
)


# ── Routers ───────────────────────────────────────────────────────────────────

api.add_router("/auth/", auth_router, tags=["Auth"])
api.add_router("/users/", users_router, tags=["Users"])

# descomente quando confirmar os caminhos reais
# api.add_router("/churches/", churches_router, tags=["Churches"])
# api.add_router("/members/", members_router, tags=["Members"])


# ── Handlers de erro globais ──────────────────────────────────────────────────

@api.exception_handler(ValidationError)
def validation_error(request: HttpRequest, exc: ValidationError):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=422,
    )


@api.exception_handler(AuthenticationError)
def auth_error(request: HttpRequest, exc: AuthenticationError):
    return JsonResponse(
        {"detail": "Credenciais inválidas ou token expirado."},
        status=401,
    )