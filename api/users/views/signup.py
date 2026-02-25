from rest_framework.views import APIView
from users.auth import Authentication
from users.serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        auth = Authentication()
        user = auth.signup(username=username, email=email, password=password)

        serializer = UserSerializer(user)

        return Response({"user": serializer.data}, status=201)