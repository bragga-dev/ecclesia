import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from dizimus.apps.users.models.church import Church
from dizimus.apps.community.utils.generate_code import _generate_code
from dizimus.apps.community.utils.default_expiration import _default_expiration




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
    from_church = models.ForeignKey(Church, on_delete=models.PROTECT, related_name="sent_affiliation_requests",)
    to_church = models.ForeignKey(Church, on_delete=models.PROTECT, null=True, blank=True, related_name="received_affiliation_requests",)
    invited_email = models.EmailField(null=True, blank=True, max_length=100) 
    invited_church_full_name = models.CharField(max_length=255, null=True, blank=True)  
    request_type = models.CharField(max_length=20, choices=RequestType.choices,)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING,)
    code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    mode = models.CharField(choices=Mode.choices, max_length=20, blank=False)
    message = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, default=None)

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
            return f"{self.get_request_type_display()} de {self.from_church} para {self.invited_church_full_name} ({self.get_status_display()})"
        return f"{self.get_request_type_display()} de {self.from_church} para {self.to_church} ({self.get_status_display()})"

    
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
        if self.mode == self.Mode.OFFLINE:        
            if self.expires_at is None:
                self.expires_at = _default_expiration()
            
            if not self.code:
                self.code = _generate_code()
        
        elif self.mode == self.Mode.AUTHENTICATED:
            self.expires_at = None
            self.code = None
        
        if self.mode == self.Mode.OFFLINE:
            if not self.invited_email:
                raise ValidationError("Offline invites require invited_email")
            if not self.invited_church_full_name:
                raise ValidationError("Offline invites require invited_church_full_name")
            if self.to_church:
                raise ValidationError("Offline invites cannot have to_church")
        
        elif self.mode == self.Mode.AUTHENTICATED:
            if not self.to_church:
                raise ValidationError("Authenticated requests require to_church")
            if self.invited_email or self.invited_church_full_name:
                raise ValidationError("Authenticated requests cannot have offline fields")
        super().save(*args, **kwargs)