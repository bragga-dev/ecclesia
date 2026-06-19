import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from dizimus.apps.users.models.church import Church
from dizimus.apps.community.utils.generate_code import _generate_code





class ChurchAffiliationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        ACCEPTED = "accepted", "Aceito"
        REJECTED = "rejected", "Recusado"
        EXPIRED = "expired", "Expirado"
        CANCELED = "canceled", "Cancelado"
        WAITING_REGISTRATION = "waiting_registration", "Aguardando Cadastro"

    class Mode(models.TextChoices):
        AUTHENTICATED = "authenticated", "Autenticado"
        OFFLINE = "offline", "Offline"

    class RequestType(models.TextChoices):
        INVITE = "invite", "Convite"
        REQUEST = "request", "Solicitação"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    from_church = models.ForeignKey(Church, on_delete=models.PROTECT, null=True, blank=True, related_name="sent_affiliation_requests",)
    to_church = models.ForeignKey(Church, on_delete=models.PROTECT, related_name="received_affiliation_requests",)
    invited_email = models.EmailField(null=True, blank=True, max_length=100) 
    invited_church_full_name = models.CharField(max_length=255, null=True, blank=True)  
    request_type = models.CharField(max_length=20, choices=RequestType.choices,)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING,)
    code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    mode = models.CharField(choices=Mode.choices, max_length=20, blank=False)
    message = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Solicitação de Afiliação"
        verbose_name_plural = "Solicitações de Afiliação"
        constraints = [
            models.UniqueConstraint(
                fields=['from_church', 'to_church', 'status'],
                condition=models.Q(status='pending'),
                name='unique_pending_affiliation'
            )
        ]
        ordering = ['-accepted_at']

    def __str__(self):
        if self.invited_church_full_name:
            return f"{self.get_request_type_display()} de {self.from_church} para {self.invited_church_name} ({self.get_status_display()})"
        return f"{self.get_request_type_display()} de {self.from_church} para {self.to_church} ({self.get_status_display()})"

    def _generate_unique_code(self, length: int = 12) -> str:
        """Gera um código único, tentando até encontrar um não usado."""
        max_attempts = 10
        for attempt in range(max_attempts):
            code = _generate_code(length)
            if not ChurchAffiliationRequest.objects.filter(code=code).exists():
                return code
        return str(uuid.uuid4())[:12]
    
    def accept(self):
        """Aceita a solicitação de afiliação."""
        if self.status != self.Status.PENDING:
            raise ValidationError("Só é possível aceitar solicitações pendentes.")
        if self.expires_at and timezone.now() > self.expires_at:
            raise ValidationError("Esta solicitação já expirou.")
        
        self.status = self.Status.ACCEPTED
        self.save()
        # TODO: Criar a relação de afiliação entre as igrejas

    def reject(self):
        """Rejeita a solicitação de afiliação."""
        if self.status != self.Status.PENDING:
            raise ValidationError("Só é possível rejeitar solicitações pendentes.")
        self.status = self.Status.REJECTED
        self.save()

    def cancel(self):
        """Cancela a solicitação de afiliação."""
        if self.status != self.Status.PENDING:
            raise ValidationError("Só é possível cancelar solicitações pendentes.")
        self.status = self.Status.CANCELED
        self.save()

    def is_expired(self) -> bool:
        """Verifica se a solicitação está expirada."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        # Gera código apenas se não existir e for uma nova instância
        if not self.code and not self.pk:
            self.code = self._generate_unique_code()
        
        # Se tem expires_at, mas não foi definido, define para 7 dias
        if not self.expires_at and self.pk is None:
            from django.utils import timezone
            import datetime
            self.expires_at = timezone.now() + datetime.timedelta(days=7)
        
        super().save(*args, **kwargs)
