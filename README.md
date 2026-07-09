
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

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
