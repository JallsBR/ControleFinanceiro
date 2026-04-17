"""
Middleware que define o banco do tenant para a request atual.
Para rotas /api/, resolve o usuário via JWT (se houver token) e, se o usuário
tiver tenant_db_name, define o thread-local e reconfigura a conexão 'tenant'.

Gerentes autenticados podem enviar o header ``X-Financas-Subject-User`` com o id
do **cliente** (User.pk) para operar no tenant desse cliente, desde que exista
``Consultoria`` ativa entre gerente e cliente.
"""

from django.contrib.auth.models import AnonymousUser
from django.db import connections
from django.http import JsonResponse

from app.db_router import set_tenant_db_name, clear_tenant_db_name


def _set_tenant_connection(db_name: str) -> None:
    set_tenant_db_name(db_name)
    conn = connections["tenant"]
    conn.settings_dict["NAME"] = db_name
    conn.close()


class TenantDatabaseMiddleware:
    """
    Deve rodar após AuthenticationMiddleware.
    Em rotas /api/, tenta autenticar via JWT e configura o alias ``tenant``.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear_tenant_db_name()
        if hasattr(request, "_financas_subject_user"):
            delattr(request, "_financas_subject_user")
        if request.path.startswith("/api/"):
            err = self._set_tenant_from_request(request)
            if err is not None:
                return err
        try:
            return self.get_response(request)
        finally:
            clear_tenant_db_name()

    def _set_tenant_from_request(self, request):
        from rest_framework_simplejwt.authentication import JWTAuthentication

        auth = JWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result is not None:
                request.user = result[0]
        except Exception:
            pass

        user = request.user
        if not getattr(user, "is_authenticated", False) or isinstance(
            user, AnonymousUser
        ):
            return None

        request._financas_subject_user = user

        raw_subject = request.headers.get("X-Financas-Subject-User", "").strip()
        if not raw_subject:
            if getattr(user, "tenant_db_name", None):
                _set_tenant_connection(user.tenant_db_name)
            return None

        try:
            subject_id = int(raw_subject)
        except ValueError:
            return JsonResponse(
                {"detail": "Cabeçalho X-Financas-Subject-User inválido."},
                status=400,
            )

        if subject_id == user.pk:
            if getattr(user, "tenant_db_name", None):
                _set_tenant_connection(user.tenant_db_name)
            return None

        if not getattr(user, "is_gerente", False):
            return JsonResponse(
                {
                    "detail": "Apenas gerentes podem usar o cabeçalho X-Financas-Subject-User."
                },
                status=403,
            )

        from django.contrib.auth import get_user_model
        from users.models import Consultoria

        User = get_user_model()
        try:
            cliente = User.objects.using("default").get(pk=subject_id)
        except User.DoesNotExist:
            return JsonResponse({"detail": "Cliente não encontrado."}, status=404)

        allowed = Consultoria.objects.using("default").filter(
            gerente=user,
            cliente=cliente,
            status=Consultoria.Status.ATIVA,
        ).exists()
        if not allowed:
            return JsonResponse(
                {"detail": "Sem consultoria ativa com este cliente."},
                status=403,
            )

        db_name = getattr(cliente, "tenant_db_name", None) or None
        if not db_name:
            return JsonResponse(
                {"detail": "Cliente sem base de dados de finanças configurada."},
                status=400,
            )

        request._financas_subject_user = cliente
        _set_tenant_connection(db_name)
        return None
