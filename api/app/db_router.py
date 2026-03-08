"""
Router que direciona o app financas para o banco do tenant (por usuário)
quando o usuário possui tenant_db_name; caso contrário usa default.
"""

import threading

# Thread-local: nome do banco do tenant para a request atual (setado pelo middleware).
_tenant_db = threading.local()

# Durante signup, o signal de categorias iniciais é pulado; as categorias são criadas no tenant em _create_tenant_db_for_user.
_skip_categorias_signal = threading.local()

# Durante migrate --database=tenant: rotear users e financas para tenant (para a migration criar_icones funcionar).
_migrate_tenant = threading.local()


def set_tenant_db_name(db_name):
    _tenant_db.name = db_name


def set_migrate_tenant(value):
    _migrate_tenant.value = value


def get_migrate_tenant():
    return getattr(_migrate_tenant, "value", False)


def set_skip_categorias_signal(value):
    _skip_categorias_signal.value = value


def get_skip_categorias_signal():
    return getattr(_skip_categorias_signal, "value", False)


def get_tenant_db_name():
    return getattr(_tenant_db, "name", None)


def clear_tenant_db_name():
    if hasattr(_tenant_db, "name"):
        del _tenant_db.name


class TenantRouter:
    """
    Para modelos do app 'financas': usa o alias 'tenant' se o usuário atual
    tiver tenant_db_name; senão 'default'.
    Para 'users' e demais apps: sempre 'default'.
    """

    def db_for_read(self, model, **hints):
        if get_migrate_tenant():
            if model._meta.app_label in ("financas", "users"):
                return "tenant"
        if model._meta.app_label == "financas":
            return "tenant" if get_tenant_db_name() else "default"
        return "default"

    def db_for_write(self, model, **hints):
        if get_migrate_tenant():
            if model._meta.app_label in ("financas", "users"):
                return "tenant"
        if model._meta.app_label == "financas":
            return "tenant" if get_tenant_db_name() else "default"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        # Permitir User (users) <-> modelos financas: no tenant há cópia do user com mesmo id (created_by).
        a, b = obj1._meta.app_label, obj2._meta.app_label
        if {a, b} == {"users", "financas"}:
            return True
        if a == "financas" and b == "financas":
            return True
        if a != "financas" and b != "financas":
            return True
        return False

    def allow_migrate(self, db, app_label, **hints):
        # Tenant recebe schema completo (auth, users, financas, etc.) para FKs e migrate.
        if db == "tenant":
            return True
        return db == "default"
