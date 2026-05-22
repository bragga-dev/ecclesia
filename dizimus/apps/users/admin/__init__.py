"""
Admin — Configuração avançada do Django Admin.
"""
from .user import UserAdmin
from .church import ChurchAdmin
from .member import MemberAdmin
from .address import ChurchAddressAdmin, MemberAddressAdmin
from .member_church import MemberChurchAdmin
from .filters import *  # Opcional: exporta os filtros
from .actions import *   # Opcional: exporta as ações
from .inlines import *   # Opcional: exporta os inlines

# Os registros já estão nos arquivos via @admin.register()
# Este __init__.py apenas garante que os módulos sejam carregados