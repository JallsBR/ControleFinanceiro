import re
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed, APIException, ValidationError
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import connections
from django.core.management import call_command

from app.db_router import set_tenant_db_name, set_skip_categorias_signal, set_migrate_tenant
from financas.service import criar_categorias_iniciais
from .models import User


def _create_tenant_db_for_user(created_user):
    """
    Cria um banco MySQL dedicado ao usuário e aplica as migrations.
    Em falha, remove o banco criado e re-lança a exceção (a transação do default reverte o user).
    """
    base_name = settings.DATABASES["default"]["NAME"]
    db_name = f"{base_name}_user_{created_user.id}"
    if not re.match(r"^[a-zA-Z0-9_]+$", db_name):
        raise APIException("Nome do banco do tenant inválido.")
    created = False
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4")
        created = True
        conn = connections["tenant"]
        conn.settings_dict["NAME"] = db_name
        conn.close()
        # Thread-local tenant + migrate_tenant para que a migration 0003 (criar_icones) use User e Icone no tenant
        set_tenant_db_name(db_name)
        set_migrate_tenant(True)
        try:
            call_command("migrate", database="tenant", run_syncdb=True)
        finally:
            set_migrate_tenant(False)
        # Copia o usuário para o tenant DB para que FKs (created_by) funcionem
        created_user.save(using="tenant")
        # Categorias iniciais no tenant (o signal foi pulado no signup)
        set_tenant_db_name(db_name)
        conn = connections["tenant"]
        conn.settings_dict["NAME"] = db_name
        conn.close()
        criar_categorias_iniciais(created_user)
        created_user.tenant_db_name = db_name
        created_user.save(update_fields=["tenant_db_name"])
    except Exception:
        if created:
            try:
                with connections["default"].cursor() as cursor:
                    cursor.execute(f"DROP DATABASE `{db_name}`")
            except Exception:
                pass
        raise


class Authentication:
    def signin(self, login=None, password=None):
        exception_auth = AuthenticationFailed("Credenciais incorretas")
        if not login or not password:
            raise exception_auth

        login = login.strip()
        user = User.objects.filter(
            Q(email__iexact=login) | Q(username__iexact=login)
        ).first()

        if user is None:
            raise exception_auth

        if not check_password(password, user.password):
            raise exception_auth

        return user
    
    def signup(self, username, email, password ):
        if not username or username == '':
            raise APIException('O nome de usuário não deve ser null')
        
        if not email or email == '':
            raise APIException('O email não deve ser null')
        
        if not password or password == '':
            raise APIException('O password não deve ser null') 
        
        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            raise ValidationError("Credenciais inválidas.")

        set_skip_categorias_signal(True)
        try:
            created_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            _create_tenant_db_for_user(created_user)
            return created_user
        finally:
            set_skip_categorias_signal(False)
    
