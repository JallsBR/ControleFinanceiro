"""
Utilitários de banco: criar banco inicial se não existir (para MySQL).
Usado antes do migrate para evitar erro "Unknown database".
"""

import os
import re

from django.conf import settings


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
        # O entrypoint do MySQL só faz GRANT em MYSQL_DATABASE; se NAME for outro, o user do Docker fica sem acesso.
        if mu and re.match(r"^[a-zA-Z0-9_]+$", mu):
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{name}`.* TO %s@'%'",
                (mu,),
            )
            cursor.execute("FLUSH PRIVILEGES")
    conn.close()
