from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from users.services import autenticar_signin


class SigninThrottle(AnonRateThrottle):
    scope = "auth_signin"


class Signin(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SigninThrottle]

    def post(self, request):
        login = (request.data.get("login") or request.data.get("email") or "").strip()
        password = request.data.get("password")

        if not login or not password:
            return Response(
                {"detail": "Login e senha são obrigatórios."},
                status=HTTP_400_BAD_REQUEST,
            )

        payload = autenticar_signin(login=login, password=password)
        return Response(payload)
