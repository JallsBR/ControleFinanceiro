"""GET /api/v1/auth/termos-uso/atual e aceite obrigatório no signup."""

from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import AceiteTermoUso, User


@pytest.mark.django_db
def test_get_termos_uso_atual(termo_uso_vigente):
    client = APIClient()
    url = reverse("termos_uso_atual")
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["version"] == "1.0.0"
    assert "conteudo" in resp.data
    assert len(resp.data["conteudo"]) > 100


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_post_signup_exige_aceite_termo(mock_tenant, termo_uso_vigente):
    mock_tenant.return_value = None
    client = APIClient()
    url = reverse("signup")
    payload = {
        "username": "sem_termo",
        "email": "sem_termo@example.com",
        "password": "SenhaSegura123!",
    }
    resp = client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "termo_aceite" in resp.data


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_post_signup_registra_aceite(mock_tenant, termo_uso_vigente):
    mock_tenant.return_value = None
    client = APIClient()
    url = reverse("signup")
    payload = {
        "username": "com_termo",
        "email": "com_termo@example.com",
        "password": "SenhaSegura123!",
        "termo_versao": "1.0.0",
        "termo_aceite": True,
    }
    resp = client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    u = User.objects.get(username="com_termo")
    assert AceiteTermoUso.objects.filter(user=u, termo=termo_uso_vigente).exists()
