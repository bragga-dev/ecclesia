
from typing import Optional
from datetime import datetime

from dizimus.apps.community.models.church_in_church_model import ChurchAffiliationRequest
from dizimus.apps.users.models.church import Church



def create_affiliation_between_church(
    *,
    from_church: Church,
    request_type: ChurchAffiliationRequest.RequestType,
    mode: ChurchAffiliationRequest.Mode,
    status: ChurchAffiliationRequest.Status = ChurchAffiliationRequest.Status.PENDING,

    to_church: Optional[Church] = None,
    invited_email: Optional[str] = None,
    invited_church_full_name: Optional[str] = None,

    code: Optional[str] = None,
    message: Optional[str] = None,
    accepted_at: Optional[datetime] = None,
    expires_at: Optional[datetime] = None,
) -> ChurchAffiliationRequest:

    return ChurchAffiliationRequest.objects.create(
        from_church=from_church,
        to_church=to_church,
        invited_email=invited_email,
        invited_church_full_name=invited_church_full_name,
        request_type=request_type,
        status=status,
        mode=mode,
        code=code,
        message=message,
        accepted_at=accepted_at,
        expires_at=expires_at,
    )

def update_affiliation_between_church(church_affiliation: ChurchAffiliationRequest,  **fields,) -> ChurchAffiliationRequest:
    allowed_fields = {field.name  for field in church_affiliation._meta.fields}

    invalid = set(fields) - allowed_fields

    if invalid:
        raise ValueError(f"Campos inválidos: {', '.join(invalid)}")
    for attr, value in fields.items():
        setattr(church_affiliation, attr, value)
    church_affiliation.full_clean()
    church_affiliation.save(update_fields=list(fields.keys()))
    return church_affiliation


def delete_affiliation_between_church(church_affiliation: ChurchAffiliationRequest,) -> None:
    church_affiliation.delete()