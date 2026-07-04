from django.core.management.base import BaseCommand
from django.db import transaction
from ecclesia.apps.users.models.system_permission import SystemPermission
from ecclesia.apps.users.models.constants import PermissionCode, PERMISSION_METADATA


class Command(BaseCommand):
    help = 'Sincroniza as permissões do sistema com o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria feito, sem alterar o banco'
        )
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            help='Desativa permissões que existem no banco mas não estão no código'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        deactivate_missing = options.get('deactivate_missing', False)
        
        self.stdout.write(self.style.SUCCESS('🔄 Sincronizando permissões...'))
        
        # 1. Obtém todos os códigos definidos no código
        defined_codes = set(PermissionCode.__dict__.values())
        defined_codes = {c for c in defined_codes if not c.startswith('__')}
        
        # 2. Busca todas as permissões existentes no banco
        existing_permissions = {
            p.code: p for p in SystemPermission.objects.all()
        }
        existing_codes = set(existing_permissions.keys())
        
        # 3. Novas permissões a criar
        to_create = defined_codes - existing_codes
        
        # 4. Permissões a desativar (existem no banco mas não no código)
        to_deactivate = existing_codes - defined_codes
        
        # 5. Permissões a atualizar (metadados mudaram)
        to_update = []
        for code in defined_codes.intersection(existing_codes):
            perm = existing_permissions[code]
            metadata = PERMISSION_METADATA.get(code, {})
            
            needs_update = False
            if metadata.get('name') and perm.name != metadata['name']:
                needs_update = True
            if metadata.get('module') and perm.module != metadata['module']:
                needs_update = True
            if metadata.get('description') and perm.description != metadata['description']:
                needs_update = True
            
            if needs_update:
                to_update.append((perm, metadata))
        
        # ──────────────────────────────────────────────────────────────────────
        # Relatório
        # ──────────────────────────────────────────────────────────────────────
        
        if to_create:
            self.stdout.write(f'\n📝 Permissões a criar ({len(to_create)}):')
            for code in sorted(to_create):
                metadata = PERMISSION_METADATA.get(code, {})
                self.stdout.write(f'  ✅ {code} - {metadata.get("name", "Sem nome")}')
        else:
            self.stdout.write('\n✅ Nenhuma nova permissão para criar.')
        
        if to_deactivate and deactivate_missing:
            self.stdout.write(f'\n⚠️  Permissões a desativar ({len(to_deactivate)}):')
            for code in sorted(to_deactivate):
                self.stdout.write(f'  ❌ {code} - {existing_permissions[code].name}')
        elif to_deactivate:
            self.stdout.write(f'\n⚠️  Permissões órfãs no banco ({len(to_deactivate)}). Use --deactivate-missing para desativá-las.')
            for code in sorted(to_deactivate):
                self.stdout.write(f'  ⚠️  {code} - {existing_permissions[code].name}')
        
        if to_update:
            self.stdout.write(f'\n🔄 Permissões a atualizar ({len(to_update)}):')
            for perm, metadata in to_update:
                self.stdout.write(f'  🔄 {perm.code}: "{perm.name}" → "{metadata.get("name", perm.name)}"')
        else:
            self.stdout.write('\n✅ Nenhuma permissão precisa ser atualizada.')
        
        # ──────────────────────────────────────────────────────────────────────
        # Execução
        # ──────────────────────────────────────────────────────────────────────
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  Modo dry-run: Nenhuma alteração foi feita.'))
            return
        
        with transaction.atomic():
            # Criar novas permissões
            for code in to_create:
                metadata = PERMISSION_METADATA.get(code, {})
                SystemPermission.objects.create(
                    code=code,
                    name=metadata.get('name', code),
                    module=metadata.get('module', 'general'),
                    description=metadata.get('description', ''),
                    is_active=True
                )
                self.stdout.write(f'  ✅ Criada: {code}')
            
            # Atualizar permissões existentes
            for perm, metadata in to_update:
                if metadata.get('name'):
                    perm.name = metadata['name']
                if metadata.get('module'):
                    perm.module = metadata['module']
                if metadata.get('description'):
                    perm.description = metadata['description']
                perm.save()
                self.stdout.write(f'  🔄 Atualizada: {perm.code}')
            
            # Desativar permissões órfãs (se solicitado)
            if deactivate_missing:
                for code in to_deactivate:
                    perm = existing_permissions[code]
                    perm.is_active = False
                    perm.save()
                    self.stdout.write(f'  ❌ Desativada: {code}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sincronização concluída!'))
        
        total = len(to_create) + len(to_update) + (len(to_deactivate) if deactivate_missing else 0)
        self.stdout.write(f'📊 Total de alterações: {total}')


#python manage.py sync_permissions --dry-run