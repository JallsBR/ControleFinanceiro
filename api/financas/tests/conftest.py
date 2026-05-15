"""Fixtures específicos do app financas (fixtures gerais em ``api/conftest.py``)."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from app.db_router import set_skip_categorias_signal
from users.models import User


def _bearer_headers(user):
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}


@pytest.fixture
def usuario_sem_categorias_iniciais(db):
    """Utilizador novo sem categorias seed (signal ignorado)."""
    set_skip_categorias_signal(True)
    try:
        return User.objects.create_user(
            username="user_sem_cat",
            email="semcat@example.com",
            password="SenhaSegura123!",
            is_active=True,
        )
    finally:
        set_skip_categorias_signal(False)


@pytest.fixture
def client_autenticado_sem_categorias(api_client, usuario_sem_categorias_iniciais):
    api_client.credentials(**_bearer_headers(usuario_sem_categorias_iniciais))
    return api_client
