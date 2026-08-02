import logging
import re

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.management import call_command
from django.db import connections
from django.db.models import Q
from django.db.utils import OperationalError
from rest_framework.exceptions import APIException, AuthenticationFailed, ValidationError

from app.db_router import set_migrate_tenant, set_skip_categorias_signal, set_tenant_db_name
from financas.service import criar_categorias_iniciais

from .models import User

logger = logging.getLogger(__name__)


def _mensagem_erro_privilegio_mysql(exc: Exception) -> str | None:
    """Traduz erros comuns de privilégio MySQL no provisionamento do tenant."""
    errno = None
    if isinstance(exc, OperationalError) and getattr(exc, "args", None):
        errno = exc.args[0]
    raw = str(exc).lower()
    if errno in (1044, 1142) or "command denied" in raw or "access denied" in raw:
        return (
            "Falha ao provisionar o banco do usuário: o usuário MySQL da aplicação "
            "precisa de CREATE/DROP em *.* e ALL no padrão `{DB_NAME}_user_%`. "
            "Ver docs/branch-auto-db-per-user.md."
        )
    if errno == 1049 or "unknown database" in raw:
        return "Banco do tenant não encontrado após a criação. Tente novamente."
    return None


def _create_tenant_db_for_user(created_user):
    """
    Cria um banco MySQL dedicado ao usuário e aplica as migrations.
    Em falha, remove o banco criado e re-lança a exceção.
    O caller (signup) remove o User no default se este método falhar.
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
        # Thread-local tenant + migrate_tenant para financas/users no alias tenant (router).
        set_tenant_db_name(db_name)
        set_migrate_tenant(True)
        try:
            call_command("migrate", database="tenant", verbosity=0)
        finally:
            set_migrate_tenant(False)
        # Copia o usuário para o tenant DB para que FKs (created_by) funcionem.
        # Caller deve manter skip_categorias_signal=True (signup / provisionar_tenants).
        created_user.save(using="tenant")
        # Categorias iniciais no tenant (o signal foi pulado no signup)
        set_tenant_db_name(db_name)
        conn = connections["tenant"]
        conn.settings_dict["NAME"] = db_name
        conn.close()
        criar_categorias_iniciais(created_user)
        created_user.tenant_db_name = db_name
        created_user.save(update_fields=["tenant_db_name"])
    except Exception as exc:
        logger.exception(
            "Falha ao provisionar tenant db=%s user_id=%s",
            db_name,
            getattr(created_user, "id", None),
        )
        if created:
            try:
                with connections["default"].cursor() as cursor:
                    cursor.execute(f"DROP DATABASE `{db_name}`")
            except Exception:
                logger.exception("Falha ao dropar banco órfão %s", db_name)
        msg = _mensagem_erro_privilegio_mysql(exc)
        if msg:
            raise APIException(msg) from exc
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

        if not user.is_active:
            raise exception_auth

        return user

    def signup(self, username, email, password):
        if not username or username == "":
            raise APIException("O nome de usuário não deve ser null")

        if not email or email == "":
            raise APIException("O email não deve ser null")

        if not password or password == "":
            raise APIException("O password não deve ser null")

        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            raise ValidationError("Credenciais inválidas.")

        set_skip_categorias_signal(True)
        try:
            # create_user antes do DDL. CREATE DATABASE no MySQL faz commit implícito,
            # então em falha no tenant removemos o user explicitamente (além do DROP DATABASE).
            created_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            try:
                _create_tenant_db_for_user(created_user)
            except Exception:
                User.objects.filter(pk=created_user.pk).delete()
                raise
            return created_user
        finally:
            set_skip_categorias_signal(False)
