from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from users.services import confirmar_redefinicao_senha, solicitar_redefinicao_senha


class PasswordResetRequestThrottle(AnonRateThrottle):
    scope = "auth_password_reset"


class PasswordResetConfirmThrottle(AnonRateThrottle):
    scope = "auth_password_reset_confirm"


class PasswordResetRequest(APIView):
    """Solicita e-mail com link para redefinir a senha."""

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request):
        login = (
            request.data.get("login")
            or request.data.get("email")
            or ""
        ).strip()
        if not login:
            return Response(
                {"detail": "Informe o e-mail ou nome de usuário."},
                status=HTTP_400_BAD_REQUEST,
            )
        payload = solicitar_redefinicao_senha(login=login)
        return Response(payload)


class PasswordResetConfirm(APIView):
    """Confirma o token do e-mail e define a nova senha."""

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request):
        challenge_id = request.data.get("challenge_id")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        confirm = request.data.get("new_password_confirm")

        if not challenge_id or not token:
            return Response(
                {"detail": "challenge_id e token são obrigatórios."},
                status=HTTP_400_BAD_REQUEST,
            )
        if not new_password:
            return Response(
                {"detail": "Informe a nova senha."},
                status=HTTP_400_BAD_REQUEST,
            )
        if confirm is not None and str(confirm) != str(new_password):
            return Response(
                {"new_password_confirm": "A confirmação deve ser igual à nova senha."},
                status=HTTP_400_BAD_REQUEST,
            )

        payload = confirmar_redefinicao_senha(
            challenge_id=str(challenge_id),
            token=str(token),
            new_password=str(new_password),
        )
        return Response(payload)
