"""
Verification API — endpoints de confirmação de email com redirecionamento.
"""
from ninja import Router
from django.http import HttpResponseRedirect
from django.conf import settings
from ecclesia.apps.users.schemas.users_schemas import MessageOut 
from ecclesia.apps.users.services.verification import verify_email
from ecclesia.apps.users.exceptions import InvalidToken
from django_ratelimit.decorators import ratelimit

router = Router()


@router.get("/verify-email/{uidb64}/{token}", summary="Confirmar e-mail",  description="Confirma o email e redireciona para o frontend.",
    auth=None,
)
@ratelimit( key="ip", rate="20/h", block=True,)
def verify_email_endpoint(request, uidb64: str, token: str):
    """
    Confirma o email e redireciona para o frontend.
    """
    try:
        user = verify_email(uidb64, token)
        # Redireciona para o frontend com mensagem de sucesso
        redirect_url = f"{settings.FRONTEND_URL}/verificacao-concluida?status=success&email={user.email}"
        return HttpResponseRedirect(redirect_url)
    except InvalidToken as e:
        # Redireciona com mensagem de erro
        redirect_url = f"{settings.FRONTEND_URL}/verificacao-concluida?status=error&message={str(e)}"
        return HttpResponseRedirect(redirect_url)
    
@router.post("/resend-verification", response={200: MessageOut, 404: MessageOut}, summary="Reenviar email de verificação",
    auth=None,  # Ou com auth se quiser proteger
)
@ratelimit(key="ip", rate="3/h", block=True,)
def resend_verification_email(request, email: str):
    """
    Reenvia o email de verificação para um usuário não verificado.
    """
    from ecclesia.apps.users.selectors import get_user_by_email
    from ecclesia.apps.users.tasks.verification import send_verification_email
    
    user = get_user_by_email(email)
    if not user or user.is_active:
        return 404, {"detail": "Usuário não encontrado ou já verificado."}
    
    send_verification_email.delay(user.pk)
    return 200, {"detail": "Email de verificação reenviado com sucesso."}