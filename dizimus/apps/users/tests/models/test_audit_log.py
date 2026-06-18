"""
Testes do AuditLog
──────────────────
Cobre: criação de logs de auditoria, relacionamentos com User, e __str__.
"""

import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestAuditLog:

    def test_audit_log_criado_com_sucesso(self, member_user, admin_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(
            action="user_created",
            user=member_user,
            performed_by=admin_user,
            reason="Criação de usuário",
            details={"source": "registration"},
        )
        assert log.pk is not None
        assert log.timestamp is not None

    def test_audit_log_user_e_one_to_one(self, member_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(
            action="login",
            user=member_user,
        )
        # Verifica o related_name
        assert member_user.audit_logs == log
        assert log.user == member_user

    def test_nao_pode_criar_dois_audit_logs_para_mesmo_user(self, member_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        AuditLog.objects.create(action="login", user=member_user)
        
        with pytest.raises(IntegrityError):
            AuditLog.objects.create(action="logout", user=member_user)

    def test_performed_by_pode_ser_nulo(self, member_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(
            action="system_action",
            user=member_user,
            performed_by=None,
        )
        assert log.performed_by is None

    def test_performed_by_pode_ser_qualquer_user(self, member_user, admin_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(
            action="admin_action",
            user=member_user,
            performed_by=admin_user,
        )
        assert log.performed_by == admin_user

    def test_str_retorna_informacoes_do_log(self, member_user, admin_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(
            action="user_updated",
            user=member_user,
            performed_by=admin_user,
        )
        expected = f"user_updated - {member_user.email} by {admin_user.email} ({log.timestamp:%Y-%m-%d %H:%M})"
        assert str(log) == expected

    def test_str_sem_performed_by(self, member_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(
            action="user_created",
            user=member_user,
        )
        expected = f"user_created - {member_user.email} ({log.timestamp:%Y-%m-%d %H:%M})"
        assert str(log) == expected

    def test_details_padrao_e_dict_vazio(self, member_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        log = AuditLog.objects.create(action="test", user=member_user)
        assert log.details == {}

    def test_details_pode_armazenar_dados_estruturados(self, member_user):
        from dizimus.apps.users.models.audit_user_model import AuditLog
        
        details = {
            "ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "changes": {"field": "value"},
        }
        log = AuditLog.objects.create(
            action="update",
            user=member_user,
            details=details,
        )
        assert log.details == details

    def test_ordering_por_timestamp_decrescente(self, member_user):
        """
        Testa que os logs são ordenados por timestamp decrescente (mais recente primeiro).
        Como AuditLog tem OneToOneField com User, usamos users diferentes.
        """
        from dizimus.apps.users.models.audit_user_model import AuditLog
        from dizimus.apps.users.models.user import User
        import time
        
        # Criamos users diferentes porque é OneToOne
        outro_user = User.objects.create_user(email="outro@teste.com", role="member")
        terceiro_user = User.objects.create_user(email="terceiro@teste.com", role="member")
        
        log1 = AuditLog.objects.create(action="first", user=member_user)
        time.sleep(0.1)  # Pequeno delay para garantir timestamps diferentes
        log2 = AuditLog.objects.create(action="second", user=outro_user)
        time.sleep(0.1)
        log3 = AuditLog.objects.create(action="third", user=terceiro_user)
        
        # Verifica a ordenação (mais recente primeiro)
        logs = list(AuditLog.objects.all())
        assert logs[0].timestamp >= logs[1].timestamp
        assert logs[1].timestamp >= logs[2].timestamp
        
        # Verifica que a ordem é por timestamp decrescente (configurado no Meta)
        assert logs[0].action == "third"  # O mais recente
        assert logs[1].action == "second"
        assert logs[2].action == "first"  # O mais antigo