"""
Utilitários de banco: criar banco inicial se não existir (para MySQL).
Usado antes do migrate para evitar erro "Unknown database".
"""

import logging
import os
import re

from django.conf import settings

logger = logging.getLogger(__name__)


def ensure_tenant_create_privileges():
    """
    Garante que o DB_USER consiga criar/migrar bancos `{DB_NAME}_user_%`.

    Requer MYSQL_ROOT_PASSWORD no ambiente (API). Sem root, só registra aviso —
    o GRANT precisa ter sido aplicado no MySQL (ver docs/branch-auto-db-per-user.md).
    """
    db = settings.DATABASES.get("default", {})
    engine = db.get("ENGINE", "")
    if "mysql" not in engine:
        return

    app_user = (db.get("USER") or "").strip()
    base_name = (db.get("NAME") or "").strip()
    if not app_user or not base_name:
        return
    if not re.match(r"^[a-zA-Z0-9_]+$", app_user):
        return
    if not re.match(r"^[a-zA-Z0-9_]+$", base_name):
        return

    # Escape de _ no padrão GRANT do MySQL (_ e % são wildcards de privilégio).
    base_escaped = base_name.replace("\\", "\\\\").replace("_", "\\_").replace("%", "\\%")
    # Padrão literal: {DB_NAME}_user_%  →  {escaped}\_user\_%
    tenant_pattern = f"{base_escaped}\\_user\\_%"

    root_pw = os.getenv("MYSQL_ROOT_PASSWORD", "").strip()
    if not root_pw:
        logger.warning(
            "MYSQL_ROOT_PASSWORD ausente: não foi possível garantir GRANT de tenant "
            "para %s (padrão %s_user_%%).",
            app_user,
            base_name,
        )
        return

    import pymysql

    host = db.get("HOST", "localhost")
    port = int(db.get("PORT", 3306))
    conn = pymysql.connect(
        user="root",
        password=root_pw,
        host=host,
        port=port,
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cursor:
            # Sem placeholders: evita conflito do % wildcard do GRANT com o escaping do driver.
            safe_user = app_user.replace("`", "")
            cursor.execute(f"GRANT CREATE, DROP ON *.* TO `{safe_user}`@'%'")
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{base_name}`.* TO `{safe_user}`@'%'"
            )
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{tenant_pattern}`.* TO `{safe_user}`@'%'"
            )
            cursor.execute("FLUSH PRIVILEGES")
        logger.info(
            "Privilégios de tenant garantidos para %s@%% (padrão %s_user_%%).",
            app_user,
            base_name,
        )
    finally:
        conn.close()


def ensure_default_database_exists():
    """
    Cria o banco padrão (NAME do default) se não existir.
    Só age quando ENGINE é MySQL; usa conexão sem database e executa
    CREATE DATABASE IF NOT EXISTS.
    """
    db = settings.DATABASES.get("default", {})
    engine = db.get("ENGINE", "")
    if "mysql" not in engine:
        return
    name = db.get("NAME", "").strip()
    if not name:
        return
    if not re.match(r"^[a-zA-Z0-9_]+$", name):
        return
    import pymysql
    from pymysql.err import OperationalError

    host = db.get("HOST", "localhost")
    port = int(db.get("PORT", 3306))
    kw = {"host": host, "port": port, "charset": "utf8mb4"}

    # Docker: o entrypoint já cria MYSQL_DATABASE e o utilizador MYSQL_USER com acesso.
    # Ligação TCP como root falha em alguns volumes; tentar primeiro o utilizador da app.
    mu, mp = os.getenv("MYSQL_USER", "").strip(), os.getenv("MYSQL_PASSWORD", "").strip()
    if mu and mp:
        try:
            c = pymysql.connect(user=mu, password=mp, database=name, **kw)
            c.close()
            return
        except OperationalError as exc:
            if not exc.args:
                raise
            errno = exc.args[0]
            # 1044 = sem privilégio nessa base; 1045 = credenciais; 1049 = base inexistente
            if errno not in (1044, 1045, 1049):
                raise

    root_pw = os.getenv("MYSQL_ROOT_PASSWORD", "").strip()
    if root_pw:
        user, password = "root", root_pw
    else:
        user = db.get("USER", "root")
        password = db.get("PASSWORD", "") or ""

    conn = pymysql.connect(user=user, password=password, **kw)
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4")
        # O entrypoint do MySQL já faz GRANT de MYSQL_USER sobre MYSQL_DATABASE. Só precisamos
        # de GRANT extra quando DB_NAME difere de MYSQL_DATABASE (senão o MySQL 8 pode devolver
        # 1410 "not allowed to create a user with GRANT" se o utilizador do .env não existir na instância).
        mysql_database = os.getenv("MYSQL_DATABASE", "").strip()
        if (
            mu
            and re.match(r"^[a-zA-Z0-9_]+$", mu)
            and mysql_database
            and name != mysql_database
        ):
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{name}`.* TO %s@'%%'",
                (mu,),
            )
            cursor.execute("FLUSH PRIVILEGES")
    conn.close()
