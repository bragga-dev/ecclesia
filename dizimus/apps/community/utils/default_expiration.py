
from django.utils import timezone
from datetime import timedelta


def _default_expiration():
    return timezone.now() + timedelta(days=7)


