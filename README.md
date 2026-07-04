Aqui está o README.md reformulado e melhorado, com uma estrutura mais profissional e informativa para o projeto Ecclesia.

```markdown
# Ecclesia

> Sistema de gestão de igrejas e comunidades

![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DD0031?style=flat&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=flat&logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)

---

## 📋 Sobre o Projeto

**Ecclesia** é uma plataforma completa para gestão de igrejas, desenvolvida com foco em escalabilidade, segurança e facilidade de uso. O sistema oferece ferramentas para gerenciamento de membros, contribuições financeiras, emissão de recibos, relatórios gerenciais e integração com gateways de pagamento.

### 🎯 Principais Funcionalidades

- **Gestão de Membros** — Cadastro, perfis, histórico e acompanhamento
- **Contribuições Financeiras** — Dízimos, ofertas e doações com suporte a múltiplos métodos
- **Emissão de Recibos** — Geração automática de recibos fiscais e de contribuição
- **Dashboard Gerencial** — Painéis analíticos com métricas e gráficos
- **Relatórios Personalizados** — Filtros avançados e exportação de dados
- **Integração com Pagamentos** — Conexão com a plataforma Asaas para pagamentos recorrentes
- **Webhooks** — Processamento assíncrono de eventos externos

---

## 🛠 Stack Tecnológica

| Camada             | Tecnologias                                             |
| ------------------ | ------------------------------------------------------- |
| **Backend**        | Django · Django Ninja · Pydantic · Celery               |
| **Banco de Dados** | PostgreSQL · Redis (cache e fila)                       |
| **Armazenamento**  | MinIO (S3 Compatível)                                   |
| **Infraestrutura** | Docker · Docker Compose · Nginx · Gunicorn · Whitenoise |
| **Testes**         | Pytest · pytest-django · pytest-cov                     |
| **Linguagem**      | Python 3.11+                                            |

---

## 🏗 Arquitetura do Projeto

### Estrutura de Diretórios

```
ecclesia/
│
├── 📄 .env
├── 📄 .env.example
├── 📄 manage.py
├── 📄 Dockerfile
├── 📄 docker-compose.dev.yml
├── 📄 docker-compose.prod.yml
│
├── 📁 requirements/
│   ├── base.txt         # Dependências principais
│   ├── dev.txt          # Dependências de desenvolvimento
│   └── prod.txt         # Dependências de produção
│
├── 📁 config/           # Configurações do projeto
│   ├── settings/        # Settings por ambiente
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── test.py
│   ├── celery.py        # Configuração do Celery
│   ├── urls.py
│   └── api.py           # Roteador principal da API
│
├── 📁 apps/             # Módulos da aplicação
│   ├── core/            # Funcionalidades essenciais
│   ├── churches/        # Gerenciamento de igrejas
│   ├── users/           # Autenticação e perfis
│   ├── members/         # Cadastro e gestão de membros
│   ├── contributions/   # Contribuições financeiras
│   ├── payments/        # Integração com gateways
│   ├── receipts/        # Emissão de recibos
│   ├── reports/         # Relatórios e análises
│   ├── dashboards/      # Painéis gerenciais
│   ├── webhooks/        # Processamento de webhooks
│   └── integrations/    # Integrações externas
│       └── asaas/       # Gateway de pagamentos
│
├── 📁 docker/           # Configurações Docker
│   ├── django/
│   │   └── entrypoint.sh
│   ├── nginx/
│   │   └── default.conf
│   ├── postgres/
│   └── redis/
│
├── 📁 minio/            # Dados do MinIO
│   └── data/
│
├── 📁 templates/        # Templates HTML
├── 📁 static/           # Arquivos estáticos
├── 📁 media/            # Arquivos de mídia (uploads)
├── 📁 logs/             # Logs da aplicação
└── 📁 scripts/          # Scripts utilitários
```

### Estrutura Interna dos Apps

Cada app segue uma arquitetura baseada em **separação de responsabilidades** e **Domain-Driven Design (DDD)**:

```
apps/users/                     # Exemplo: App de usuários
│
├── 📁 admin/                  # Configuração do Django Admin
│   ├── user_admin.py
│   ├── group_admin.py
│   └── __init__.py
│
├── 📁 api/                    # Endpoints da API (Django Ninja)
│   ├── auth.py
│   ├── profile.py
│   ├── verification.py
│   ├── password_reset.py
│   └── sessions.py
│
├── 📁 schemas/                # Schemas Pydantic (validação/serialização)
│   ├── auth.py
│   ├── profile.py
│   ├── verification.py
│   └── common.py
│
├── 📁 models/                 # Modelos do banco de dados
│   ├── user.py
│   ├── profile.py
│   ├── session.py
│   └── security_event.py
│
├── 📁 services/               # Regras de negócio
│   ├── auth/                  # Autenticação
│   ├── profile/               # Gerenciamento de perfis
│   ├── verification/          # Verificação de e-mail
│   └── password_reset/        # Recuperação de senha
│
├── 📁 repositories/           # Camada de persistência
│   ├── users.py
│   ├── profiles.py
│   └── sessions.py
│
├── 📁 selectors/              # Queries e leitura de dados
│   ├── users.py
│   ├── profiles.py
│   └── sessions.py
│
├── 📁 tasks/                  # Tarefas assíncronas (Celery)
│   ├── emails.py
│   ├── cleanup.py
│   └── security.py
│
├── 📁 tokens/                 # Geração/validação de tokens
│   ├── email_verification.py
│   ├── password_reset.py
│   └── jwt.py
│
├── 📁 permissions/            # Controle de permissões
│   ├── roles.py
│   ├── auth.py
│   └── ownership.py
│
├── 📁 validators/             # Validadores customizados
│   ├── password.py
│   ├── username.py
│   └── image.py
│
├── 📁 exceptions/             # Exceções customizadas
│   ├── auth.py
│   ├── verification.py
│   └── profile.py
│
├── 📁 constants/              # Constantes do domínio
│   ├── roles.py
│   ├── auth.py
│   └── limits.py
│
├── 📁 filters/                # Filtros de consulta
│   └── users.py
│
├── 📁 signals/                # Eventos do Django (signals)
│   ├── auth.py
│   └── profile.py
│
├── 📁 utils/                  # Utilitários
│   ├── slug.py
│   ├── ip.py
│   └── device.py
│
├── 📁 tests/                  # Testes
│   ├── factories/             # Factories para testes
│   ├── unit/                  # Testes unitários
│   ├── integration/           # Testes de integração
│   └── e2e/                   # Testes end-to-end
│
├── 📁 migrations/             # Migrações do Django
│
├── 📄 apps.py                 # Configuração do app
├── 📄 urls.py                 # Rotas do app
└── 📄 __init__.py
```

### 📊 Responsabilidade dos Arquivos

| Arquivo           | Camada  | Responsabilidade |
| ----------------- | ------- | ---------------- |
| `models.py`       | 📦 Dados | Definição dos modelos do banco de dados |
| `repositories.py` | 📦 Dados | Persistência e acesso ao banco de dados |
| `selectors.py`    | 📦 Dados | Queries otimizadas para leitura de dados |
| `schemas.py`      | 📡 API   | Schemas Pydantic para validação e serialização |
| `api.py`          | 📡 API   | Definição dos endpoints da API |
| `filters.py`      | 📡 API   | Filtros avançados para listagens |
| `permissions.py`  | 📡 API   | Controle de permissões e acesso |
| `services.py`     | 🧠 Negócio | Regras de negócio e orquestração |
| `tasks.py`        | ⚡ Negócio | Tarefas assíncronas do Celery |
| `signals.py`      | 🔔 Eventos | Hooks para eventos do Django |
| `constants.py`    | 🔧 Infra   | Constantes e enums do domínio |
| `exceptions.py`   | 🔧 Infra   | Exceções customizadas da aplicação |

### 🎨 Princípios de Design

1. **Clean Architecture** — Separação clara entre camadas
2. **Repository Pattern** — Abstração da persistência
3. **Service Layer** — Centralização das regras de negócio
4. **Dependency Inversion** — Módulos dependem de abstrações
5. **Single Responsibility** — Cada arquivo tem um propósito específico

---

## 🚀 Ambientes

### Desenvolvimento

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/ecclesia.git
cd ecclesia

# Copiar arquivo de ambiente
cp .env.example .env

# Subir ambiente com Docker
docker compose -f docker-compose.dev.yml up --build
```

### Produção

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Comandos Úteis

```bash
# Migrações
docker compose exec web python manage.py migrate

# Criar superusuário
docker compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker compose exec web python manage.py collectstatic

# Executar Celery worker (local)
celery -A config worker -l info

# Executar Celery beat (agendador)
celery -A config beat -l info

# Acessar shell do Django
docker compose exec web python manage.py shell
```

---

## 🗄 MinIO (Armazenamento)

| Interface             | URL                     |
| --------------------- | ----------------------- |
| Painel Administrativo | `http://localhost:9001` |
| Endpoint S3           | `http://localhost:9000` |

Credenciais padrão (altere no `.env`):
- **Access Key:** `minioadmin`
- **Secret Key:** `minioadmin`

---

## 🧪 Testes

### Instalação de Dependências

**Pip:**
```bash
pip install pytest pytest-django pytest-cov factory-boy
```

**Poetry:**
```bash
poetry add --group dev pytest pytest-django pytest-cov factory-boy
```

### Executando os Testes

| Comando | Descrição |
| ------- | --------- |
| `pytest` | Rodar todos os testes |
| `pytest --cov=ecclesia --cov-report=term-missing` | Testes com relatório de cobertura |
| `pytest -vv` | Modo verboso |
| `pytest -s` | Mostrar prints/logs |
| `pytest -x` | Parar no primeiro erro |
| `pytest --lf` | Reexecutar apenas testes que falharam |

### Testes por App

```bash
# App de usuários
pytest ecclesia/apps/users/tests/

# App de membros
pytest ecclesia/apps/members/tests/

# App de contribuições
pytest ecclesia/apps/contributions/tests/
```

### Testes por Módulo

```bash
# Schemas
pytest ecclesia/apps/users/tests/schemas/ --cov=ecclesia.apps.users.schemas --cov-report=term-missing

# Models
pytest ecclesia/apps/users/tests/models/ --cov=ecclesia.apps.users.models --cov-report=term-missing

# Services
pytest ecclesia/apps/users/tests/services/ --cov=ecclesia.apps.users.services --cov-report=term-missing

# Validators
pytest ecclesia/apps/users/tests/validators/ --cov=ecclesia.apps.users.validators --cov-report=term-missing
```

### Testes Específicos

```bash
# Arquivo específico
pytest ecclesia/apps/users/tests/models/test_user.py

# Classe específica
pytest ecclesia/apps/users/tests/models/test_user.py::TestUserModel

# Método específico
pytest ecclesia/apps/users/tests/models/test_user.py::TestUserModel::test_create_user
```

### Relatório de Cobertura HTML

```bash
pytest --cov=ecclesia --cov-report=html
xdg-open htmlcov/index.html   # Linux/Mac
# ou
start htmlcov/index.html       # Windows
```

### Configuração do Coverage

Adicione ao `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "*/migrations/*",
    "*/config/*",
    "*/tests/*",
    "*/admin.py",
    "*/apps.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Estrutura Recomendada de Testes

```
apps/users/tests/
├── __init__.py
├── conftest.py           # Fixtures compartilhadas
├── factories/            # Factories para testes
│   ├── user_factory.py
│   └── profile_factory.py
├── unit/                 # Testes unitários
│   ├── models/
│   ├── services/
│   ├── validators/
│   └── utils/
├── integration/          # Testes de integração
│   ├── api/
│   └── repositories/
└── e2e/                  # Testes end-to-end
    └── auth_flow.py
```

### 📝 Boas Práticas

- ✅ Testar **regras de negócio** antes da interface
- ✅ Priorizar testes de: `services` > `validators` > `models`
- ✅ Utilizar factories e fixtures reutilizáveis
- ✅ Evitar testes frágeis baseados em textos HTML
- ✅ Manter **coverage acima de 80%**
- ✅ Seguir a estrutura: **Arrange → Act → Assert (AAA)**
- ✅ Usar `pytest.mark.parametrize` para múltiplos cenários

---

## 🎯 Objetivos da Arquitetura

| Objetivo | Descrição |
| -------- | --------- |
| 📈 **Alta escalabilidade** | Estrutura modular preparada para crescimento horizontal |
| 🔍 **Separação de responsabilidades** | Cada arquivo tem um papel claro e bem definido |
| 🔧 **Fácil manutenção** | Organização previsível em todos os apps |
| 🧩 **Preparação para microsserviços** | Apps independentes e desacoplados |
| 🚀 **Pronto para produção** | Docker, Nginx, Gunicorn e Whitenoise configurados |
| 🔒 **Segurança por design** | JWT, verificação de e-mail, rate limiting e boas práticas |

---

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add some amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📧 Contato

- **Autor:** [Seu Nome]
- **Email:** seu.email@exemplo.com
- **Projeto:** [github.com/seu-usuario/ecclesia](https://github.com/seu-usuario/ecclesia)

---

<div align="center">
  <sub>Built with ❤️ for the community</sub>
</div>
```

---

### Principais Melhorias Realizadas:

1. **Estrutura Visual Aprimorada** — Uso de emojis, badges e separadores visuais para melhor legibilidade
2. **Seção "Sobre o Projeto"** — Descrição clara do propósito e funcionalidades principais
3. **Organização Hierárquica** — Diretórios representados com ícones e estrutura mais clara
4. **Tabelas Informativas** — Responsabilidades, comandos e boas práticas em tabelas
5. **Princípios de Design** — Explicação dos padrões arquiteturais utilizados
6. **Instruções Detalhadas** — Comandos mais completos e bem organizados
7. **Boas Práticas de Testes** — Estrutura recomendada e dicas de qualidade
8. **Guia de Contribuição** — Processo padrão para contribuições
9. **Design Profissional** — Visual mais moderno e convidativo
10. **Informações de Contato** — Adicionado rodapé com contato e licença