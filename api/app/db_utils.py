"""
Utilitários de banco: criar banco inicial se não existir (para MySQL).
Usado antes do migrate para evitar erro "Unknown database".
"""

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
    conn = pymysql.connect(
        host=db.get("HOST", "localhost"),
        port=int(db.get("PORT", 3306)),
        user=db.get("USER", "root"),
        password=db.get("PASSWORD", ""),
        charset="utf8mb4",
    )
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4")
    conn.close()
