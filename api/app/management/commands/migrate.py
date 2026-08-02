"""
Comando migrate que garante a existência do banco padrão (MySQL) antes de rodar.
Executa CREATE DATABASE IF NOT EXISTS no início (parâmetros do .env), assim
os system checks e a conexão não falham com "Unknown database".
"""

from django.core.management.commands.migrate import Command as MigrateCommand

from app.db_utils import ensure_default_database_exists, ensure_tenant_create_privileges


class Command(MigrateCommand):
    def run_from_argv(self, argv):
        ensure_default_database_exists()
        ensure_tenant_create_privileges()
        super().run_from_argv(argv)
