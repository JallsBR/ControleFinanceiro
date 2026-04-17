from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserProfileUpdateSerializer, UserSerializer


class UserProfileView(APIView):
    """GET e PATCH do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        serializer = UserSerializer(user)
        return Response({'user': serializer.data})

    def patch(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user.refresh_from_db()
        return Response(
            {'user': UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
