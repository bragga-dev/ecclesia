from django.utils.translation import gettext_lazy as _


class PermissionDenied(Exception):
    def __init__(self, msg: str = "Você não tem permissão para realizar esta ação."):
        super().__init__(_(msg))