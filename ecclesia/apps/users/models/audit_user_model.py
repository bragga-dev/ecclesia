# ecclesia/apps/audit/models.py
import uuid
from django.db import models
from ecclesia.apps.users.models.user import User

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=100) 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="audit_logs",)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="actions_performed")
    reason = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        performed = f" by {self.performed_by.email}" if self.performed_by else ""
        return f"{self.action} - {self.user.email}{performed} ({self.timestamp:%Y-%m-%d %H:%M})"
