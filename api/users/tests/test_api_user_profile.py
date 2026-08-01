"""GET/PATCH do perfil autenticado (Tipo 2 + PATCH parcial — /api/v1/auth/user)."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


@pytest.mark.django_db
def test_get_user_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("user"))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_user_success(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.get(reverse("user"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "user" in body
    u = body["user"]
    assert u["id"] == usuario_comum.id
    assert u["email"] == usuario_comum.email
    assert u["username"] == usuario_comum.username
    assert "pagina_inicial" in u


@pytest.mark.django_db
def test_patch_user_unauthenticated(api_client):
    resp = api_client.patch(
        reverse("user"), {"first_name": "Novo"}, format="json"
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_partial_update_success(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.patch(
        reverse("user"),
        {"first_name": "NomeAtualizado"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    usuario_comum.refresh_from_db()
    assert usuario_comum.first_name == "NomeAtualizado"
    assert resp.json()["user"]["first_name"] == "NomeAtualizado"


@pytest.mark.django_db
def test_patch_partial_update_validation_email_duplicado(
    client_autenticado_comum, usuario_comum, outro_usuario_comum
):
    resp = client_autenticado_comum.patch(
        reverse("user"),
        {"email": outro_usuario_comum.email},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in resp.json()


@pytest.mark.django_db
def test_patch_partial_update_validation_pagina_inicial_nao_permitida(
    client_autenticado_comum,
):
    resp = client_autenticado_comum.patch(
        reverse("user"),
        {"pagina_inicial": User.PaginaInicial.ADMINISTRAR},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "pagina_inicial" in resp.json()


@pytest.mark.django_db
def test_get_user_inclui_two_factor_enabled(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.get(reverse("user"))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["user"]["two_factor_enabled"] is False


@pytest.mark.django_db
def test_patch_ativar_2fa_exige_senha_atual(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.patch(
        reverse("user"),
        {"two_factor_enabled": True},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "current_password" in resp.json()
    usuario_comum.refresh_from_db()
    assert usuario_comum.two_factor_enabled is False


@pytest.mark.django_db
def test_patch_ativar_2fa_com_senha_ok(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.patch(
        reverse("user"),
        {
            "two_factor_enabled": True,
            "current_password": "SenhaSegura123!",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["user"]["two_factor_enabled"] is True
    usuario_comum.refresh_from_db()
    assert usuario_comum.two_factor_enabled is True


@pytest.mark.django_db
def test_patch_desativar_2fa_com_senha_ok(client_autenticado_comum, usuario_comum):
    usuario_comum.two_factor_enabled = True
    usuario_comum.save(update_fields=["two_factor_enabled"])
    resp = client_autenticado_comum.patch(
        reverse("user"),
        {
            "two_factor_enabled": False,
            "current_password": "SenhaSegura123!",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["user"]["two_factor_enabled"] is False
