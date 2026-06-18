"""
Admin — Configuração avançada do Django Admin.
"""
from .user import UserAdmin
from .church import ChurchAdmin
from .member import MemberAdmin
from .address import ChurchAddressAdmin, MemberAddressAdmin
from .audit_log import AuditLogAdmin
from .filters import *
from .actions import *
from .inlines import *

# Os registros já estão nos arquivos via @admin.register()
# Este __init__.py apenas garante que os módulos sejam carregados