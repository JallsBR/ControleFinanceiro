"""
Serializer de refresh JWT que busca o usuário sempre no banco default (central).
Evita 500 quando o usuário foi deletado ou o token é inválido e retorna 401.
"""

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model


class TokenRefreshSerializerDefaultDB(TokenRefreshSerializer):
    """
    Igual ao TokenRefreshSerializer, mas força a busca do usuário no banco default.
    Necessário quando há DATABASE_ROUTERS (ex.: tenant por usuário) para que
    o refresh não tente buscar User em outro banco.
    """

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)

        if user_id:
            User = get_user_model()
            try:
                user = User.objects.using("default").get(
                    **{api_settings.USER_ID_FIELD: user_id}
                )
            except User.DoesNotExist:
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )
            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()
            data["refresh"] = str(refresh)

        return data
