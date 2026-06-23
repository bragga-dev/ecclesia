from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from dizimus.apps.community.models.church_in_church_model import ChurchAffiliationRequest
from dizimus.apps.users.models.church import Church
from dizimus.apps.community.schemas.church_in_church_schema import (
ChurchAffiliationOfflineAcceptOut,
ChurchAffiliationOfflineAcceptIn,
)

from dizimus.apps.community.repositories.church_in_church_repository import (
    create_affiliation_between_church,
    update_affiliation_between_church,
    delete_affiliation_between_church,
)

from dizimus.apps.community.selectors.church_in_church_selector import (
    get_affiliated_churche_by_id,
    is_church_already_affiliated,
    has_pending_affiliation_with_church,
)


def create_authenticated_invite(*, from_church: Church, to_church: Church,  message: str | None = None,) -> ChurchAffiliationRequest:
    """ Cria um convite autenticado entre duas igrejas. """
    
    # 1. Verifica se as igrejas são diferentes
    if from_church.id == to_church.id:
        raise ValidationError("Uma igreja não pode enviar um convite para si mesma.")
    
    # 2. Verifica se já existe uma afiliação ativa entre as igrejas
    if is_church_already_affiliated(from_church.id, to_church.id):
        raise ValidationError("As igrejas já possuem uma afiliação ativa.")
    
    # 3. Verifica se já existe um convite pendente entre as igrejas
    if has_pending_affiliation_with_church(from_church.id, to_church.id):
        raise ValidationError("Já existe um convite pendente entre estas igrejas.")
    
    # 4. Verifica se existe um convite pendente no sentido inverso
    if has_pending_affiliation_with_church(to_church.id, from_church.id):
        raise ValidationError("A igreja destino já possui um convite pendente para a igreja origem.")
    
    # 5. Verifica se a igreja destino está ativa
    if not to_church.user.is_active:
        raise ValidationError("Não é possível enviar convite para uma igreja inativa.")
    
    # 6. Verifica se a igreja origem está ativa
    if not from_church.user.is_active:
        raise ValidationError("Não é possível enviar convite de uma igreja inativa.")
    
    invite = create_affiliation_between_church(
        from_church=from_church,
        to_church=to_church,
        request_type=ChurchAffiliationRequest.RequestType.INVITE,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.AUTHENTICATED,
        message=message,
    )
    
    return invite

def create_offline_invite(*, from_church: Church, message: str | None = None,  invited_email: str, invited_church_full_name: str) -> ChurchAffiliationRequest:
    try:
        validate_email(invited_email)
    except ValidationError:
        raise ValidationError("Email inválido!")
        
    return create_affiliation_between_church(
        from_church=from_church,
        invited_email=invited_email,
        invited_church_full_name=invited_church_full_name,
        request_type=ChurchAffiliationRequest.RequestType.INVITE,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.OFFLINE,
        message=message,
    )


def create_affiliation_request(*, from_church: Church, to_church: Church, message: str | None = None) -> ChurchAffiliationRequest:
    return create_affiliation_between_church(
        from_church=from_church,
        to_church=to_church,
        request_type=ChurchAffiliationRequest.RequestType.REQUEST,
        status=ChurchAffiliationRequest.Status.PENDING,
        mode=ChurchAffiliationRequest.Mode.AUTHENTICATED,
        message=message,
    )