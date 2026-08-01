from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from users.services import verificar_otp_login


class TwoFactorVerifyThrottle(AnonRateThrottle):
    scope = "auth_2fa_verify"


class TwoFactorVerify(APIView):
    """Conclui o login após OTP numérico ou link mágico do e-mail."""

    permission_classes = [AllowAny]
    throttle_classes = [TwoFactorVerifyThrottle]

    def post(self, request):
        challenge_id = request.data.get("challenge_id")
        code = request.data.get("code")
        link_token = request.data.get("link_token")

        code_ok = code is not None and str(code).strip() != ""
        link_ok = link_token is not None and str(link_token).strip() != ""

        if not challenge_id:
            return Response(
                {"detail": "challenge_id é obrigatório."},
                status=HTTP_400_BAD_REQUEST,
            )
        if code_ok == link_ok:
            return Response(
                {"detail": "Informe exatamente um entre code e link_token."},
                status=HTTP_400_BAD_REQUEST,
            )

        payload = verificar_otp_login(
            challenge_id=str(challenge_id),
            code=str(code) if code_ok else None,
            link_token=str(link_token) if link_ok else None,
        )
        return Response(payload)
