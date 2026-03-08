"""
Middleware que define o banco do tenant para a request atual.
Para rotas /api/, resolve o usuário via JWT (se houver token) e, se o usuário
tiver tenant_db_name, define o thread-local e reconfigura a conexão 'tenant'.
"""

from django.db import connections
from app.db_router import set_tenant_db_name, clear_tenant_db_name, get_tenant_db_name


class TenantDatabaseMiddleware:
    """
    Deve rodar após AuthenticationMiddleware.
    Em rotas /api/, tenta autenticar via JWT e, se o usuário tiver tenant_db_name,
    configura a conexão 'tenant' e o thread-local para o router.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear_tenant_db_name()
        if request.path.startswith("/api/"):
            self._set_tenant_from_request(request)
        try:
            return self.get_response(request)
        finally:
            clear_tenant_db_name()

    def _set_tenant_from_request(self, request):
        # Resolve usuário via JWT para ter request.user disponível antes da view
        from rest_framework_simplejwt.authentication import JWTAuthentication
        auth = JWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result is not None:
                request.user = result[0]
        except Exception:
            pass
        if getattr(request.user, "is_authenticated", False) and getattr(
            request.user, "tenant_db_name", None
        ):
            db_name = request.user.tenant_db_name
            set_tenant_db_name(db_name)
            conn = connections["tenant"]
            conn.settings_dict["NAME"] = db_name
            conn.close()
