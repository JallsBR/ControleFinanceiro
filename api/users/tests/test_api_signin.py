"""Tipo 10 — autenticação JWT (POST /api/v1/auth/signin)."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_post_login_success(usuario_comum):
    client = APIClient()
    url = reverse("signin")
    resp = client.post(
        url,
        {"login": usuario_comum.email, "password": "SenhaSegura123!"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "access" in body and "refresh" in body
    assert body["user"]["id"] == usuario_comum.id
    assert body["user"]["email"] == usuario_comum.email


@pytest.mark.django_db
def test_post_login_success_with_username(usuario_comum):
    client = APIClient()
    url = reverse("signin")
    resp = client.post(
        url,
        {"login": usuario_comum.username, "password": "SenhaSegura123!"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["user"]["username"] == usuario_comum.username


@pytest.mark.django_db
def test_post_login_invalid(usuario_comum):
    client = APIClient()
    url = reverse("signin")
    resp = client.post(
        url,
        {"login": usuario_comum.email, "password": "senha_errada"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_login_inactive_user(usuario_inativo):
    client = APIClient()
    url = reverse("signin")
    resp = client.post(
        url,
        {"login": usuario_inativo.email, "password": "SenhaSegura123!"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_login_missing_credentials(usuario_comum):
    client = APIClient()
    url = reverse("signin")
    resp = client.post(url, {"login": usuario_comum.email}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "obrigatórios" in resp.json().get("detail", "").lower()
