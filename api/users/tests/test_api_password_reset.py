"""Recuperação de senha por e-mail."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from users.models import PasswordResetChallenge
from users.services import PASSWORD_RESET_GENERIC_MSG


@pytest.mark.django_db
def test_password_reset_request_envia_email(usuario_comum, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.FRONTEND_URL = "http://localhost:2488"

    client = APIClient()
    with patch("users.services.secrets.token_urlsafe", return_value="token-reset-fixo"):
        resp = client.post(
            reverse("password_reset_request"),
            {"login": usuario_comum.email},
            format="json",
        )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["detail"] == PASSWORD_RESET_GENERIC_MSG
    assert len(mail.outbox) == 1
    assert usuario_comum.email in mail.outbox[0].to
    assert "token-reset-fixo" in mail.outbox[0].body
    assert "/auth/redefinir-senha" in mail.outbox[0].body
    assert mail.outbox[0].alternatives
    assert PasswordResetChallenge.objects.filter(user=usuario_comum).count() == 1


@pytest.mark.django_db
def test_password_reset_request_email_inexistente_nao_vaza(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    client = APIClient()
    resp = client.post(
        reverse("password_reset_request"),
        {"login": "naoexiste@example.com"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["detail"] == PASSWORD_RESET_GENERIC_MSG
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_password_reset_confirm_success(usuario_comum, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.FRONTEND_URL = "http://localhost:2488"
    client = APIClient()

    with patch("users.services.secrets.token_urlsafe", return_value="abc123token"):
        client.post(
            reverse("password_reset_request"),
            {"login": usuario_comum.username},
            format="json",
        )
    desafio = PasswordResetChallenge.objects.filter(user=usuario_comum).latest("created_at")

    resp = client.post(
        reverse("password_reset_confirm"),
        {
            "challenge_id": str(desafio.id),
            "token": "abc123token",
            "new_password": "NovaSenhaSegura456!",
            "new_password_confirm": "NovaSenhaSegura456!",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    usuario_comum.refresh_from_db()
    assert usuario_comum.check_password("NovaSenhaSegura456!")
    desafio.refresh_from_db()
    assert desafio.consumed_at is not None

    login = client.post(
        reverse("signin"),
        {"login": usuario_comum.email, "password": "NovaSenhaSegura456!"},
        format="json",
    )
    assert login.status_code == status.HTTP_200_OK
    assert "access" in login.json() or login.json().get("requires_2fa")


@pytest.mark.django_db
def test_password_reset_confirm_token_invalido(usuario_comum):
    desafio = PasswordResetChallenge.objects.create(
        user=usuario_comum,
        token_hash=make_password("certo"),
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    client = APIClient()
    resp = client.post(
        reverse("password_reset_confirm"),
        {
            "challenge_id": str(desafio.id),
            "token": "errado",
            "new_password": "NovaSenhaSegura456!",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_password_reset_confirm_expirado(usuario_comum):
    desafio = PasswordResetChallenge.objects.create(
        user=usuario_comum,
        token_hash=make_password("tok"),
        expires_at=timezone.now() - timedelta(minutes=1),
    )
    client = APIClient()
    resp = client.post(
        reverse("password_reset_confirm"),
        {
            "challenge_id": str(desafio.id),
            "token": "tok",
            "new_password": "NovaSenhaSegura456!",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
