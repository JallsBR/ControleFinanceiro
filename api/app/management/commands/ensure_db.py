"""
Cria o banco padrão (DB_NAME do .env) se não existir.
Útil antes da primeira migration; o comando migrate já chama isso automaticamente.
"""

from django.core.management.base import BaseCommand

from app.db_utils import ensure_default_database_exists


class Command(BaseCommand):
    help = "Cria o banco padrão (MySQL) se não existir; usa parâmetros do .env/settings."

    def handle(self, *args, **options):
        ensure_default_database_exists()
        self.stdout.write(self.style.SUCCESS("Banco padrão garantido (CREATE DATABASE IF NOT EXISTS)."))
