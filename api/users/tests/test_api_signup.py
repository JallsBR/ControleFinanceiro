"""POST /api/v1/auth/signup — criação de conta (mock do provisionamento de tenant MySQL)."""

from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_post_signup_success(mock_tenant, termo_uso_vigente):
    mock_tenant.return_value = None
    client = APIClient()
    url = reverse("signup")
    payload = {
        "username": "novo_cadastro",
        "email": "novo_cadastro@example.com",
        "password": "SenhaSegura123!",
        "termo_versao": "1.0.0",
        "termo_aceite": True,
    }
    resp = client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    mock_tenant.assert_called_once()
    u = User.objects.get(username="novo_cadastro")
    assert u.email == payload["email"]
    assert u.check_password(payload["password"])


@pytest.mark.django_db
def test_post_signup_validation_duplicate_username(usuario_comum, termo_uso_vigente):
    client = APIClient()
    url = reverse("signup")
    resp = client.post(
        url,
        {
            "username": usuario_comum.username,
            "email": "outro_email_unico@example.com",
            "password": "SenhaSegura123!",
            "termo_versao": "1.0.0",
            "termo_aceite": True,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_post_signup_validation_duplicate_email(usuario_comum, termo_uso_vigente):
    client = APIClient()
    url = reverse("signup")
    resp = client.post(
        url,
        {
            "username": "username_totalmente_novo",
            "email": usuario_comum.email,
            "password": "SenhaSegura123!",
            "termo_versao": "1.0.0",
            "termo_aceite": True,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_post_signup_validation_required_empty_username(mock_tenant, termo_uso_vigente):
    mock_tenant.return_value = None
    client = APIClient()
    url = reverse("signup")
    resp = client.post(
        url,
        {"username": "", "email": "e@example.com", "password": "SenhaSegura123!"},
        format="json",
    )
    assert resp.status_code >= status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_post_signup_validation_required_empty_password(mock_tenant, termo_uso_vigente):
    mock_tenant.return_value = None
    client = APIClient()
    url = reverse("signup")
    resp = client.post(
        url,
        {"username": "u_valido", "email": "e2@example.com", "password": ""},
        format="json",
    )
    assert resp.status_code >= status.HTTP_400_BAD_REQUEST
