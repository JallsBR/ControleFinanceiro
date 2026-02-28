"""
Middleware para desabilitar verificação CSRF em rotas da API (JWT).
Evita 403 em requisições cross-origin do frontend.
"""


class DisableCSRFForAPI:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):
            request._dont_enforce_csrf_checks = True
        return self.get_response(request)
