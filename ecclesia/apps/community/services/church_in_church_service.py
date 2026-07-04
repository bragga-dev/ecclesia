"""
Church In Church Service — lógica de negócio de afiliações.
"""

import uuid
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string


from ecclesia.apps.users.models.church import Church
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.repositories.church import create_church_profile
from ecclesia.apps.users.repositories.user import create_user, activate_user
from ecclesia.apps.users.selectors.church_selector import get_church_by_id
from ecclesia.apps.users.services.auth import _make_tokens


from ecclesia.apps.community.models.church_in_church_model import ChurchAffiliationRequest

from ecclesia.apps.community.repositories.church_in_church_repository import (
    create_affiliation_between_church,
    delete_affiliation_between_church,
    update_affiliation_between_church,
)
from ecclesia.apps.community.selectors.church_in_church_selector import (
    get_affiliated_churche_by_id,
    get_church_affiliation_request_by_id,
    get_offline_invites_by_code,
    validate_church_can_affiliation_request,
    validate_church_can_authenticated_invite,
    validate_church_can_be_offline_invited,
    get_affiliation_requests_with_prefetch,
    get_affiliation_requests_with_prefetch,
    get_affiliation_stats,
    amply_church_in_church_filters,
    search_church_in_church_selector,
    get_all_expires_at,

)


from ecclesia.apps.community.tasks.send_affiliation_offline_accepted import send_affiliation_offline_accepted
from ecclesia.apps.community.tasks.send_affiliation_offline_invite import send_affiliation_offline_invite
from ecclesia.apps.community.tasks.send_affiliation_online_invite import send_affiliation_online_invite
from ecclesia.apps.community.tasks.send_affiliation_request import send_affiliation_request
from ecclesia.apps.community.tasks.send_confirme_affiliation_online_invite import send_confirme_affiliation_online_invite
from ecclesia.apps.community.tasks.send_affiliation_accepted_to_parish import send_affiliation_accepted_to_parish
from ecclesia.apps.community.tasks.send_affiliation_rejected_to_parish import send_affiliation_rejected_to_parish
from ecclesia.apps.community.tasks.send_affiliation_cancelled_to_parish import send_affiliation_cancelled_to_parish
from ecclesia.apps.community.tasks.check_offline_invite_expiration import check_offline_invite_expiration


from ecclesia.apps.community.utils.generate_temp_password import _generate_temp_password


# =========================================================================
# PARÓQUIA -> COMUNIDADE ONLINE
# =========================================================================
def create_authenticated_invite(
    *,
    from_church_id: uuid.UUID,
    to_church_id: uuid.UUID,
    message: str | None = None,
) -> ChurchAffiliationRequest:
    """Cria um convite online para uma igreja já cadastrada no sistema."""
    from_church = get_church_by_id(church_id=from_church_id)
    to_church = get_church_by_id(church_id=to_church_id)

    if not from_church:
        raise ValidationError("Igreja origem não encontrada")
    if not to_church:
        raise ValidationError("Igreja destino não encontrada")

    validate_church_can_authenticated_invite(from_church=from_church, to_church=to_church)

    invite = create_affiliation_between_church(
        from_church=from_church,
        to_church=to_church,
        request_type=ChurchAffiliationRequest.RequestType.INVITE,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.AUTHENTICATED,
        message=message,
    )

    send_affiliation_online_invite.delay(invite.id)
    return invite


def update_authenticated_invite(
    church_affiliation_id: uuid.UUID,
    **fields,
) -> ChurchAffiliationRequest:
    if not fields:
        raise ValueError("Nenhum campo fornecido para atualização")
    affiliation = get_church_affiliation_request_by_id(church_affiliation_id)
    if not affiliation:
        raise ChurchAffiliationRequest.DoesNotExist(
            f"O vínculo {church_affiliation_id} não foi encontrado"
        )
    affiliation_updated = update_affiliation_between_church(affiliation, **fields)
    send_confirme_affiliation_online_invite.delay(affiliation_updated.id)
    return affiliation_updated


# =========================================================================
# PARÓQUIA -> COMUNIDADE OFFLINE
# =========================================================================
def create_offline_invite(
    *,
    from_church: Church,
    message: str | None = None,
    invited_email: str,
    invited_church_full_name: str,
) -> ChurchAffiliationRequest:
    """
    Cria convite offline para uma igreja que ainda não está cadastrada.
    Envia e-mail com link de aceite — a conta só é criada quando ela aceitar.
    """
    validate_church_can_be_offline_invited(from_church, invited_email, invited_church_full_name)

    invite = create_affiliation_between_church(
        from_church=from_church,
        invited_email=invited_email,
        invited_church_full_name=invited_church_full_name,
        request_type=ChurchAffiliationRequest.RequestType.INVITE,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.OFFLINE,
        message=message,
    )
    send_affiliation_offline_invite.delay(invite.id)
    expiration_time = invite.expires_at + timedelta(seconds=1)
    check_offline_invite_expiration.apply_async(args=[invite.id], eta=expiration_time,)
    return invite

def get_pending_offline_invites(code: str) -> ChurchAffiliationRequest:
    """Retorna convites offline pendentes enviados por uma igreja."""
    invite = get_offline_invites_by_code(code)
    if not invite:
        raise ValidationError("Convite não encontrado ou já utilizado.")
    return invite


@transaction.atomic
def accept_offline_invite(*, code: str) -> dict:
    """
    A nova igreja aceita o convite. Neste momento:
      1. Valida o convite pelo code
      2. Gera senha temporária
      3. Cria User (role=CHURCH, já ativo — e-mail validado pelo convite)
      4. Cria Church com os dados preenchidos pela Sede
      5. Vincula to_church + status -> ACCEPTED
      6. Dispara e-mail de confirmação com credenciais + instrução de troca de senha
      7. Retorna tokens JWT para login automático
    """
    invite = get_offline_invites_by_code(code)
    if not invite:
        raise ValidationError("Convite não encontrado ou já utilizado.")
    if invite.is_expired():
        raise ValidationError("Este convite expirou. Entre em contato com a igreja para solicitar um novo.")
    if invite.to_church:
        raise ValidationError("Este convite já foi aceito.")
    
    temp_password = _generate_temp_password()

    user = create_user(email=invite.invited_email, password=temp_password, role=User.UserRole.CHURCH,)

    activate_user(user)

    church = create_church_profile(user, full_name=invite.invited_church_full_name, church_type=Church.ChurchType.COMMUNITY,)

    invite.to_church = church

    invite.status = ChurchAffiliationRequest.Status.ACCEPTED
    invite.accepted_at = timezone.now()
    invite.save(update_fields=["to_church", "status", "accepted_at"])
    send_affiliation_offline_accepted.delay(invite.id, temp_password)
    send_affiliation_accepted_to_parish.delay(invite.id)
    tokens = _make_tokens(user)

    return {
    **tokens,
    "affiliation_id": invite.id,
    "church_full_name": church.full_name or "",
    "from_church_name": invite.from_church.full_name or "",
    "is_new": True,
    }

# =========================================================================
# AÇÃO EM CONVITE/SOLICITAÇÃO (autenticado)
# =========================================================================
def handle_affiliation_action(
    *,
    affiliation_id: uuid.UUID,
    church: Church,
    action: str,
) -> ChurchAffiliationRequest:
    """accept/reject: to_church. cancel: from_church."""
    affiliation = get_church_affiliation_request_by_id(affiliation_id)

    if not affiliation:
        raise ValidationError("Solicitação não encontrada.")

    if action in ("accept", "reject"):
        if not affiliation.to_church or affiliation.to_church_id != church.id:
            raise PermissionError("Apenas a igreja destinatária pode aceitar ou rejeitar.")
    elif action == "cancel":
        if affiliation.from_church_id != church.id:
            raise PermissionError("Apenas a igreja remetente pode cancelar.")

    if action == "accept":
        affiliation.accept()
        send_affiliation_accepted_to_parish.delay(affiliation.id)
    elif action == "reject":
        affiliation.reject()
        send_affiliation_rejected_to_parish.delay(affiliation.id)
    elif action == "cancel":
        send_affiliation_cancelled_to_parish.delay(affiliation.id)
        affiliation.cancel()

    return affiliation


# =========================================================================
# COMUNIDADE -> ONLINE
# =========================================================================
def create_affiliation_request(
    *,
    from_church_id: uuid.UUID,
    to_church_id: uuid.UUID,
    message: str | None = None,
) -> ChurchAffiliationRequest:
    """Cria uma solicitação de afiliação de uma comunidade para uma sede."""
    from_church = get_church_by_id(church_id=from_church_id)
    to_church = get_church_by_id(church_id=to_church_id)

    if not from_church:
        raise ValidationError("Igreja origem não encontrada")
    if not to_church:
        raise ValidationError("Igreja destino não encontrada")

    validate_church_can_affiliation_request(from_church, to_church)

    invite = create_affiliation_between_church(
        from_church=from_church,
        to_church=to_church,
        request_type=ChurchAffiliationRequest.RequestType.REQUEST,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.AUTHENTICATED,
        message=message,
    )
    send_affiliation_request.delay(invite.id)
    return invite



def list_church_affiliations(
    *,
    church_id: uuid.UUID,
    filters=None,
    search: str | None = None,
):
    queryset = get_affiliation_requests_with_prefetch(church_id=church_id)

    if filters:
        queryset = amply_church_in_church_filters(queryset, filters)

    if search:
        queryset = search_church_in_church_selector(queryset, search)

    return queryset


def get_church_affiliation_stats_service(*, church_id: uuid.UUID) -> dict:
    return get_affiliation_stats(church_id=church_id)




def cancel_expired_affiliations() -> None:
    """
    Cancela automaticamente pedidos de afiliação cujo prazo expirou.
    """
    invite = get_all_expires_at()
    invite.update(status=ChurchAffiliationRequest.Status.CANCELLED)
    invite_ids = [i.id for i in invite]
    for invite_id in invite_ids:
        send_affiliation_cancelled_to_parish.delay(invite_id)   
