from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = "ecclesia.apps.users"
    label = "users"              # mantém o prefixo curto nas migrations
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Usuários"