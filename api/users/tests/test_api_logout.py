"""POST /api/v1/auth/logout — blacklist do refresh token."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_post_logout_unauthenticated():
    client = APIClient()
    resp = client.post(reverse("logout"), {}, format="json")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_logout_invalid_refresh(client_autenticado_comum):
    resp = client_autenticado_comum.post(
        reverse("logout"), {"refresh": "token-invalido"}, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_post_logout_success(client_autenticado_comum, usuario_comum):
    refresh = RefreshToken.for_user(usuario_comum)
    resp = client_autenticado_comum.post(
        reverse("logout"), {"refresh": str(refresh)}, format="json"
    )
    assert resp.status_code == status.HTTP_205_RESET_CONTENT
