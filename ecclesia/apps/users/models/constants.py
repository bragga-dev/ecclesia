# Fonte única da verdade para os valores de role armazenados no banco.
# Importado tanto por user.py quanto por user_manager.py,
# eliminando dependência circular sem duplicar strings.

ROLE_ADMIN  = "admin"
ROLE_MEMBER = "member"
ROLE_CHURCH = "church"

# ============================================================================
# PERMISSIONS - Fonte única da verdade para todas as permissões do sistema
# ============================================================================

class PermissionCode:
    """
    Códigos de permissão do sistema.
    Estes são os únicos valores aceitos no campo SystemPermission.code.
    """
    
    # ========== MEMBROS ==========
    MEMBERS_VIEW = "members.view"
    MEMBERS_CREATE = "members.create"
    MEMBERS_UPDATE = "members.update"
    MEMBERS_DELETE = "members.delete"
    MEMBERS_INVITE = "members.invite"
    MEMBERS_APPROVE = "members.approve"
    MEMBERS_ROLE_CHANGE = "members.role.change"
    
    # ========== IGREJA ==========
    CHURCH_VIEW = "church.view"
    CHURCH_UPDATE = "church.update"
    CHURCH_SETTINGS = "church.settings"
    CHURCH_INVITE = "church.invite"
    CHURCH_DELETE = "church.delete"
    
    # ========== FINANÇAS ==========
    FINANCE_VIEW = "finance.view"
    FINANCE_CREATE = "finance.create"
    FINANCE_UPDATE = "finance.update"
    FINANCE_DELETE = "finance.delete"
    FINANCE_MANAGE = "finance.manage"
    FINANCE_REPORTS = "finance.reports"
    
    # ========== EVENTOS ==========
    EVENTS_VIEW = "events.view"
    EVENTS_CREATE = "events.create"
    EVENTS_UPDATE = "events.update"
    EVENTS_DELETE = "events.delete"
    EVENTS_MANAGE = "events.manage"
    
    # ========== PERMISSÕES ==========
    PERMISSIONS_VIEW = "permissions.view"
    PERMISSIONS_MANAGE = "permissions.manage"
    
    # ========== RELATÓRIOS ==========
    REPORTS_VIEW = "reports.view"
    REPORTS_EXPORT = "reports.export"
    
    # ========== AUDIT ==========
    AUDIT_VIEW = "audit.view"
    AUDIT_EXPORT = "audit.export"


# Mapeamento de permissões para seus metadados
PERMISSION_METADATA = {
    PermissionCode.MEMBERS_VIEW: {
        "name": "Visualizar membros",
        "module": "users",
        "description": "Permite visualizar a lista de membros e seus detalhes"
    },
    PermissionCode.MEMBERS_CREATE: {
        "name": "Criar membros",
        "module": "users",
        "description": "Permite adicionar novos membros à igreja"
    },
    PermissionCode.MEMBERS_UPDATE: {
        "name": "Atualizar membros",
        "module": "users",
        "description": "Permite editar informações dos membros"
    },
    PermissionCode.MEMBERS_DELETE: {
        "name": "Deletar membros",
        "module": "users",
        "description": "Permite remover membros da igreja"
    },
    PermissionCode.MEMBERS_INVITE: {
        "name": "Convidar membros",
        "module": "users",
        "description": "Permite enviar convites para novos membros"
    },
    PermissionCode.MEMBERS_APPROVE: {
        "name": "Aprovar membros",
        "module": "users",
        "description": "Permite aprovar solicitações de membros pendentes"
    },
    PermissionCode.MEMBERS_ROLE_CHANGE: {
        "name": "Alterar cargo de membros",
        "module": "users",
        "description": "Permite alterar o cargo (role) de outros membros"
    },
    PermissionCode.CHURCH_VIEW: {
        "name": "Visualizar igreja",
        "module": "community",
        "description": "Permite visualizar informações da igreja"
    },
    PermissionCode.CHURCH_UPDATE: {
        "name": "Atualizar igreja",
        "module": "community",
        "description": "Permite editar informações da igreja"
    },
    PermissionCode.CHURCH_SETTINGS: {
        "name": "Configurações da igreja",
        "module": "community",
        "description": "Permite acessar e modificar configurações da igreja"
    },
    PermissionCode.CHURCH_INVITE: {
        "name": "Convidar igrejas",
        "module": "community",
        "description": "Permite enviar convites para outras igrejas"
    },
    PermissionCode.CHURCH_DELETE: {
        "name": "Deletar igreja",
        "module": "community",
        "description": "Permite deletar a igreja (cuidado!)"
    },
    PermissionCode.FINANCE_VIEW: {
        "name": "Visualizar finanças",
        "module": "finance",
        "description": "Permite visualizar registros financeiros"
    },
    PermissionCode.FINANCE_CREATE: {
        "name": "Criar registros financeiros",
        "module": "finance",
        "description": "Permite criar novos registros financeiros"
    },
    PermissionCode.FINANCE_UPDATE: {
        "name": "Atualizar registros financeiros",
        "module": "finance",
        "description": "Permite editar registros financeiros existentes"
    },
    PermissionCode.FINANCE_DELETE: {
        "name": "Deletar registros financeiros",
        "module": "finance",
        "description": "Permite remover registros financeiros"
    },
    PermissionCode.FINANCE_MANAGE: {
        "name": "Gerenciar finanças",
        "module": "finance",
        "description": "Permissão abrangente para gerenciar finanças"
    },
    PermissionCode.FINANCE_REPORTS: {
        "name": "Relatórios financeiros",
        "module": "finance",
        "description": "Permite gerar relatórios financeiros"
    },
    PermissionCode.EVENTS_VIEW: {
        "name": "Visualizar eventos",
        "module": "community",
        "description": "Permite visualizar eventos da igreja"
    },
    PermissionCode.EVENTS_CREATE: {
        "name": "Criar eventos",
        "module": "community",
        "description": "Permite criar novos eventos"
    },
    PermissionCode.EVENTS_UPDATE: {
        "name": "Atualizar eventos",
        "module": "community",
        "description": "Permite editar eventos existentes"
    },
    PermissionCode.EVENTS_DELETE: {
        "name": "Deletar eventos",
        "module": "community",
        "description": "Permite remover eventos"
    },
    PermissionCode.EVENTS_MANAGE: {
        "name": "Gerenciar eventos",
        "module": "community",
        "description": "Permissão abrangente para gerenciar eventos"
    },
    PermissionCode.PERMISSIONS_VIEW: {
        "name": "Visualizar permissões",
        "module": "community",
        "description": "Permite visualizar configurações de permissões"
    },
    PermissionCode.PERMISSIONS_MANAGE: {
        "name": "Gerenciar permissões",
        "module": "community",
        "description": "Permite gerenciar permissões de cargos"
    },
    PermissionCode.REPORTS_VIEW: {
        "name": "Visualizar relatórios",
        "module": "community",
        "description": "Permite visualizar relatórios gerais"
    },
    PermissionCode.REPORTS_EXPORT: {
        "name": "Exportar relatórios",
        "module": "community",
        "description": "Permite exportar relatórios em diversos formatos"
    },
    PermissionCode.AUDIT_VIEW: {
        "name": "Visualizar auditoria",
        "module": "community",
        "description": "Permite visualizar logs de auditoria"
    },
    PermissionCode.AUDIT_EXPORT: {
        "name": "Exportar auditoria",
        "module": "community",
        "description": "Permite exportar logs de auditoria"
    },
}