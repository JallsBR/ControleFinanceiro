import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def usuario_comum(db):
    return User.objects.create_user(
        username="usuario_comum",
        email="comum@example.com",
        password="SenhaSegura123!",
        is_active=True,
    )


@pytest.fixture
def usuario_inativo(db):
    return User.objects.create_user(
        username="usuario_inativo",
        email="inativo@example.com",
        password="SenhaSegura123!",
        is_active=False,
    )


@pytest.fixture
def usuario_staff(db):
    return User.objects.create_user(
        username="staff_teste",
        email="staff@example.com",
        password="SenhaSegura123!",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def outro_usuario_comum(db):
    return User.objects.create_user(
        username="outro_comum",
        email="outro@example.com",
        password="OutraSenha456!",
        is_active=True,
    )


def bearer_headers(user):
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}


@pytest.fixture
def client_autenticado_comum(api_client, usuario_comum):
    api_client.credentials(**bearer_headers(usuario_comum))
    return api_client


@pytest.fixture
def client_autenticado_staff(api_client, usuario_staff):
    api_client.credentials(**bearer_headers(usuario_staff))
    return api_client
