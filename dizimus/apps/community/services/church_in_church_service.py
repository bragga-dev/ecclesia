import uuid

from django.core.exceptions import ValidationError
from dizimus.apps.community.models.church_in_church_model import ChurchAffiliationRequest
from dizimus.apps.users.models.church import Church
from dizimus.apps.community.repositories.church_in_church_repository import (
    create_affiliation_between_church,
    update_affiliation_between_church,
    delete_affiliation_between_church,
)
from dizimus.apps.community.selectors.church_in_church_selector import (
    get_affiliated_churche_by_id,
    validate_church_can_authenticated_invite,
    validate_church_can_affiliation_request,
    validate_church_can_be_offline_invited,
)
from dizimus.apps.users.selectors.church_selector import get_church_by_id

from dizimus.apps.community.tasks.send_affiliation_offline_invite import send_affiliation_offline_invite
from dizimus.apps.community.tasks.send_affiliation_online_invite import send_affiliation_online_invite
from dizimus.apps.community.tasks.send_affiliation_request import send_affiliation_request
from dizimus.apps.community.selectors.church_in_church_selector import get_church_affiliation_request_by_id
from dizimus.apps.community.tasks.send_confirme_affiliation_online_invite import send_confirme_affiliation_online_invite

#=========================================================================
# SEDE -> COMUNIDADE ONLINE
#========================================================================
def create_authenticated_invite(*, from_church_id: uuid.UUID, to_church_id: uuid.UUID,  message: str | None = None,) -> ChurchAffiliationRequest:
    """Cria um convite online para uma igreja que está no sistema."""
    from_church = get_church_by_id(church_id=from_church_id)
    to_church = get_church_by_id(church_id=to_church_id)

    if not from_church:
        raise ValidationError("Igreja origem não encontrada")

    if not to_church:
        raise ValidationError("Igreja destino não encontrada")

    validate_church_can_authenticated_invite(
        from_church=from_church,
        to_church=to_church,
    )

    invite =  create_affiliation_between_church(
        from_church=from_church,
        to_church=to_church,
        request_type=ChurchAffiliationRequest.RequestType.INVITE,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.AUTHENTICATED,
        message=message,   
    )

    send_affiliation_online_invite.delay(invite.id)
    return invite

def update_authenticated_invite(church_affiliation_id: uuid.UUID, **fields) -> ChurchAffiliationRequest:
        if not fields:
            raise ValueError("Nenhum campo fornecido para atualização")
        afiliaton =  get_church_affiliation_request_by_id(church_affiliation_id)
        if not afiliaton:
            raise ChurchAffiliationRequest.DoesNotExist(f"O vínculo {church_affiliation_id} não foi encontrado")
        try:
            afiliaton_updated = update_affiliation_between_church(afiliaton, **fields)
            send_confirme_affiliation_online_invite.delay(afiliaton_updated.id)
            return afiliaton_updated
        except Exception as e:
             raise 


#=========================================================================
# SEDE -> COMUNIDADE OFFLINE
#========================================================================
def create_offline_invite(*, from_church: Church, message: str | None = None, invited_email: str, invited_church_full_name: str) -> ChurchAffiliationRequest:
    """Cria um convite offline para uma igreja que ainda não está no sistema."""
    validate_church_can_be_offline_invited(from_church, invited_email, invited_church_full_name)
    invite =  create_affiliation_between_church(
        from_church=from_church,
        invited_email=invited_email,
        invited_church_full_name=invited_church_full_name,
        request_type=ChurchAffiliationRequest.RequestType.INVITE,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.OFFLINE,
        message=message,
       
    )
    send_affiliation_offline_invite.delay(invite.id)
    return invite
    

#=========================================================================
# COMUNIDADE ->  ONLINE
#========================================================================
def create_affiliation_request(*, from_church_id: uuid.UUID, to_church_id: uuid.UUID, message: str | None = None) -> ChurchAffiliationRequest:
    """Cria uma solicitação de afiliação de uma comunidade para uma sede."""
    from_church = get_church_by_id(church_id=from_church_id)
    to_church = get_church_by_id(church_id=to_church_id)

    if not from_church:
            raise ValidationError("Igreja origem não encontrada")

    if not to_church:
        raise ValidationError("Igreja destino não encontrada")
    
    validate_church_can_affiliation_request(from_church, to_church)
    
    invite =  create_affiliation_between_church(
        from_church=from_church,
        to_church=to_church,
        request_type=ChurchAffiliationRequest.RequestType.REQUEST,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.AUTHENTICATED,
        message=message,
    )
    send_affiliation_request.delay(invite.id)
    return invite


