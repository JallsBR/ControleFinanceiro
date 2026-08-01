"""2FA por e-mail — signin condicional e POST /api/v1/auth/2fa/verify."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from users.models import TwoFactorChallenge
from users.services import OTP_MAX_ATTEMPTS


@pytest.mark.django_db
def test_post_login_com_2fa_retorna_challenge_sem_tokens(usuario_comum, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.FRONTEND_URL = "http://localhost:2488"
    usuario_comum.two_factor_enabled = True
    usuario_comum.save(update_fields=["two_factor_enabled"])

    client = APIClient()
    with (
        patch("users.services._gerar_otp_numerico", return_value="123456"),
        patch("users.services.secrets.token_urlsafe", return_value="link-token-fixo"),
    ):
        resp = client.post(
            reverse("signin"),
            {"login": usuario_comum.email, "password": "SenhaSegura123!"},
            format="json",
        )

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body.get("requires_2fa") is True
    assert "challenge_id" in body
    assert "access" not in body
    assert "refresh" not in body
    assert len(mail.outbox) == 1
    assert "123456" in mail.outbox[0].body
    assert "link-token-fixo" in mail.outbox[0].body
    assert "/auth/2fa-link" in mail.outbox[0].body
    assert mail.outbox[0].alternatives
    assert "text/html" in mail.outbox[0].alternatives[0][1]
    assert "123456" in mail.outbox[0].alternatives[0][0]
    assert usuario_comum.email in mail.outbox[0].to


@pytest.mark.django_db
def test_post_2fa_verify_success(usuario_comum, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    usuario_comum.two_factor_enabled = True
    usuario_comum.save(update_fields=["two_factor_enabled"])

    client = APIClient()
    with patch("users.services._gerar_otp_numerico", return_value="654321"):
        signin = client.post(
            reverse("signin"),
            {"login": usuario_comum.email, "password": "SenhaSegura123!"},
            format="json",
        )
    challenge_id = signin.json()["challenge_id"]

    resp = client.post(
        reverse("two_factor_verify"),
        {"challenge_id": challenge_id, "code": "654321"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "access" in body and "refresh" in body
    assert body["user"]["id"] == usuario_comum.id

    desafio = TwoFactorChallenge.objects.get(pk=challenge_id)
    assert desafio.consumed_at is not None


@pytest.mark.django_db
def test_post_2fa_verify_por_link_token(usuario_comum, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.FRONTEND_URL = "http://localhost:2488"
    usuario_comum.two_factor_enabled = True
    usuario_comum.save(update_fields=["two_factor_enabled"])

    client = APIClient()
    with (
        patch("users.services._gerar_otp_numerico", return_value="111222"),
        patch("users.services.secrets.token_urlsafe", return_value="meu-link-secreto"),
    ):
        signin = client.post(
            reverse("signin"),
            {"login": usuario_comum.email, "password": "SenhaSegura123!"},
            format="json",
        )
    challenge_id = signin.json()["challenge_id"]

    resp = client.post(
        reverse("two_factor_verify"),
        {"challenge_id": challenge_id, "link_token": "meu-link-secreto"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "access" in resp.json()


@pytest.mark.django_db
def test_post_2fa_verify_codigo_errado(usuario_comum, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    usuario_comum.two_factor_enabled = True
    usuario_comum.save(update_fields=["two_factor_enabled"])

    client = APIClient()
    with patch("users.services._gerar_otp_numerico", return_value="111111"):
        signin = client.post(
            reverse("signin"),
            {"login": usuario_comum.email, "password": "SenhaSegura123!"},
            format="json",
        )
    challenge_id = signin.json()["challenge_id"]

    resp = client.post(
        reverse("two_factor_verify"),
        {"challenge_id": challenge_id, "code": "000000"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    desafio = TwoFactorChallenge.objects.get(pk=challenge_id)
    assert desafio.attempts == 1
    assert desafio.consumed_at is None


@pytest.mark.django_db
def test_post_2fa_verify_expirado(usuario_comum):
    desafio = TwoFactorChallenge.objects.create(
        user=usuario_comum,
        code_hash=make_password("222222"),
        link_token_hash=make_password("tok"),
        expires_at=timezone.now() - timedelta(minutes=1),
    )
    client = APIClient()
    resp = client.post(
        reverse("two_factor_verify"),
        {"challenge_id": str(desafio.id), "code": "222222"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_2fa_verify_max_attempts(usuario_comum):
    desafio = TwoFactorChallenge.objects.create(
        user=usuario_comum,
        code_hash=make_password("333333"),
        expires_at=timezone.now() + timedelta(minutes=10),
        attempts=OTP_MAX_ATTEMPTS,
    )
    client = APIClient()
    resp = client.post(
        reverse("two_factor_verify"),
        {"challenge_id": str(desafio.id), "code": "333333"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_2fa_verify_campos_obrigatorios():
    client = APIClient()
    resp = client.post(reverse("two_factor_verify"), {}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
