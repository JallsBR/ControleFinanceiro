from rest_framework_simplejwt.views import TokenRefreshView
from users.jwt_serializers import TokenRefreshSerializerDefaultDB


class TokenRefreshViewDefaultDB(TokenRefreshView):
    """Refresh de JWT que busca o usuário sempre no banco default (evita 500 com router de tenant)."""
    serializer_class = TokenRefreshSerializerDefaultDB
