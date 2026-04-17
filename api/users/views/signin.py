from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.auth import Authentication
from users.serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class Signin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login = (request.data.get("login") or request.data.get("email") or "").strip()
        password = request.data.get("password")

        if not login or not password:
            return Response(
                {"detail": "Login e senha são obrigatórios."},
                status=HTTP_400_BAD_REQUEST,
            )

        user = Authentication.signin(self, login=login, password=password)
        
        token = RefreshToken.for_user(user)

        serializer = UserSerializer(user)

        return Response({
            "user": serializer.data,
            "refresh": str(token),
            "access": str(token.access_token)
        })