```


dizimus/
│
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── api.py
│   │
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       ├── prod.py
│       └── test.py
│
├── apps/
│   ├── core/
│   │
│   ├── churches/
│   │
│   ├── users/
│   │
│   ├── members/
│   │
│   ├── contributions/
│   │
│   ├── payments/
│   │
│   ├── receipts/
│   │
│   ├── reports/
│   │
│   ├── dashboards/
│   │
│   ├── webhooks/
│   │
│   └── integrations/
│       └── asaas/
│
├── templates/
│
├── static/
│
├── media/
│
├── logs/
│
└── scripts/
```
##  Estrutura Interna dos APPs
```
apps/members/
│
├── migrations/
│
├── admin.py
├── api.py
├── apps.py
├── models.py
├── schemas.py
├── services.py
├── selectors.py
├── repositories.py
├── tasks.py
├── permissions.py
├── filters.py
├── exceptions.py
├── constants.py
├── signals.py
├── urls.py
└── tests/
```# dizimus
