from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users import services as user_services
from users.serializers import UserSerializer


class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        termo_versao = request.data.get("termo_versao")
        termo_aceite = request.data.get("termo_aceite")

        if isinstance(termo_aceite, str):
            termo_aceite = termo_aceite.lower() in ("true", "1", "yes", "sim")

        user = user_services.cadastrar_usuario(
            username=username,
            email=email,
            password=password,
            termo_versao=termo_versao,
            termo_aceite=bool(termo_aceite) if termo_aceite is not None else None,
            request=request,
        )

        serializer = UserSerializer(user)

        return Response({"user": serializer.data}, status=201)