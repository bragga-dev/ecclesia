
from dizimus.apps.community.tasks.send_affiliation_offline_invite import send_affiliation_offline_invite
from dizimus.apps.community.tasks.send_affiliation_online_invite import send_affiliation_online_invite
from dizimus.apps.community.tasks.send_affiliation_request import send_affiliation_request
from dizimus.apps.community.tasks.send_confirme_affiliation_online_invite import send_confirme_affiliation_online_invite

__all__ = [
    "send_affiliation_offline_invite",
    "send_affiliation_online_invite",
    "send_affiliation_request",
    "send_confirme_affiliation_online_invite",
]