# ecclesia/core/decorators.py
from django_ratelimit.decorators import ratelimit

# =============================================================
# POR IP — endpoints públicos (sem autenticação)
# =============================================================

def throttle_ip(rate="10/m"):
    """Uso geral para endpoints públicos."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_login(rate="5/m"):
    """Login — restritivo para evitar brute force de senha."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_registration(rate="3/m"):
    """Registro — evita criação em massa de contas."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_password_reset(rate="3/m"):
    """Recuperação de senha — evita spam de e-mail."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_password_change(rate="5/m"):
    """Troca de senha autenticada — evita troca em loop."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_verify_email(rate="5/m"):
    """Verificação/reenvio de e-mail."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_verify_code(rate="5/m"):
    """Validação de código OTP/2FA — evita brute force de código."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_resend_code(rate="3/m"):
    """Reenvio de código OTP — mais restritivo que a validação."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_two_factor(rate="5/m"):
    """Autenticação de dois fatores."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_social_auth(rate="10/m"):
    """Login social — Google, Facebook, Apple."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_token_refresh(rate="20/m"):
    """Refresh de token JWT."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_public_read(rate="60/m"):
    """Leitura pública — listagens e detalhes sem autenticação."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_public_detail(rate="60/m"):
    """Detalhe público de um recurso específico."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_public_list(rate="30/m"):
    """Listagem pública — mais restritivo que detalhe."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_webhook(rate="120/m"):
    """Webhooks externos (ex: Asaas) — alta frequência esperada."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_health_check(rate="60/m"):
    """Health check — monitoramento externo."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_sitemap(rate="10/m"):
    """Sitemap e robots.txt — crawlers."""
    return ratelimit(key="ip", rate=rate, block=True)

def throttle_feed(rate="10/m"):
    """RSS/Atom feed."""
    return ratelimit(key="ip", rate=rate, block=True)

# =============================================================
# POR USUÁRIO — endpoints autenticados
# =============================================================

def throttle_user(rate="60/m"):
    """Uso geral para endpoints autenticados."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_upload(rate="20/m"):
    """Upload de arquivos — foto, banner, documentos."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_upload_bulk(rate="5/m"):
    """Upload em lote — múltiplos arquivos simultaneamente."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_download(rate="30/m"):
    """Download de arquivos."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_write(rate="30/m"):
    """Escrita — criação e atualização de recursos."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_create(rate="20/m"):
    """Criação de recursos — POST."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_update(rate="30/m"):
    """Atualização de recursos — PUT/PATCH."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_delete(rate="20/m"):
    """Deleção — mais restritivo para evitar destruição em massa."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_bulk_delete(rate="5/m"):
    """Deleção em lote — extremamente restritivo."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_bulk_create(rate="5/m"):
    """Criação em lote."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_bulk_update(rate="5/m"):
    """Atualização em lote."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_read(rate="120/m"):
    """Leitura autenticada — listagens e detalhes."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_list(rate="60/m"):
    """Listagem autenticada."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_detail(rate="120/m"):
    """Detalhe autenticado de um recurso."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_search(rate="30/m"):
    """Busca — evita scraping e queries pesadas em sequência."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_filter(rate="60/m"):
    """Filtros — mais liberal que busca."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_autocomplete(rate="60/m"):
    """Autocomplete — chamado a cada keystroke."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_export(rate="5/m"):
    """Exportação de dados — PDF, CSV, relatórios."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_import(rate="5/m"):
    """Importação de dados — CSV, planilhas."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_report(rate="10/m"):
    """Geração de relatórios."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_dashboard(rate="30/m"):
    """Dados de dashboard — múltiplos widgets."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_payment(rate="10/m"):
    """Pagamento e operações financeiras (Asaas)."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_payment_refund(rate="5/m"):
    """Estorno — extremamente restritivo."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_payment_method(rate="10/m"):
    """Cadastro/atualização de método de pagamento."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_subscription(rate="10/m"):
    """Operações de assinatura — criação, cancelamento."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_invoice(rate="20/m"):
    """Geração e consulta de faturas."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_notification(rate="10/m"):
    """Envio de notificações — evita spam."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_notification_read(rate="60/m"):
    """Marcar notificações como lidas."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_invite(rate="10/m"):
    """Convites — evita spam de convites."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_invite_resend(rate="3/m"):
    """Reenvio de convite."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_profile(rate="20/m"):
    """Atualização de perfil."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_settings(rate="20/m"):
    """Atualização de configurações do usuário."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_admin(rate="30/m"):
    """Endpoints administrativos — ações sensíveis."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_admin_bulk(rate="5/m"):
    """Ações administrativas em lote."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_impersonate(rate="10/m"):
    """Impersonar outro usuário — staff only."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_audit_log(rate="30/m"):
    """Consulta de logs de auditoria."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_api_key(rate="10/m"):
    """Criação e revogação de API keys."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_webhook_manage(rate="10/m"):
    """Gerenciamento de webhooks pelo usuário."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_comment(rate="10/m"):
    """Comentários — evita spam."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_reaction(rate="30/m"):
    """Reações — likes, emojis."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_share(rate="10/m"):
    """Compartilhamento de conteúdo."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_follow(rate="20/m"):
    """Seguir/deixar de seguir."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_message(rate="30/m"):
    """Envio de mensagens internas."""
    return ratelimit(key="user", rate=rate, block=True)

def throttle_chat(rate="60/m"):
    """Chat em tempo real — mais liberal."""
    return ratelimit(key="user", rate=rate, block=True)

# =============================================================
# POR USUÁRIO OU IP — endpoints semi-públicos
# =============================================================

def throttle_user_or_ip(rate="30/m"):
    """
    Usa usuário se autenticado, IP se anônimo.
    Ideal para endpoints acessíveis nos dois contextos.
    """
    return ratelimit(key="user_or_ip", rate=rate, block=True)

def throttle_contact(rate="3/m"):
    """Formulário de contato — evita spam mesmo sem login."""
    return ratelimit(key="user_or_ip", rate=rate, block=True)

def throttle_support(rate="5/m"):
    """Abertura de ticket de suporte."""
    return ratelimit(key="user_or_ip", rate=rate, block=True)

def throttle_rating(rate="10/m"):
    """Avaliação de produto/serviço."""
    return ratelimit(key="user_or_ip", rate=rate, block=True)

def throttle_review(rate="5/m"):
    """Envio de review/depoimento."""
    return ratelimit(key="user_or_ip", rate=rate, block=True)

def throttle_newsletter(rate="3/m"):
    """Inscrição em newsletter."""
    return ratelimit(key="user_or_ip", rate=rate, block=True)

def throttle_waitlist(rate="3/m"):
    """Inscrição em lista de espera."""
    return ratelimit(key="user_or_ip", rate=rate, block=True)