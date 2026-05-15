"""Testes unitários diretos em `users.auth.Authentication` (happy path + erros de domínio)."""

from unittest.mock import patch

import pytest
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from users.auth import Authentication
from users.models import User


@pytest.mark.django_db
def test_authentication_signin_success(usuario_comum):
    auth = Authentication()
    user = auth.signin(login=usuario_comum.email, password="SenhaSegura123!")
    assert user.pk == usuario_comum.pk


@pytest.mark.django_db
def test_authentication_signin_wrong_password(usuario_comum):
    auth = Authentication()
    with pytest.raises(AuthenticationFailed):
        auth.signin(login=usuario_comum.email, password="errada")


@pytest.mark.django_db
def test_authentication_signin_inactive_raises(usuario_inativo):
    auth = Authentication()
    with pytest.raises(AuthenticationFailed):
        auth.signin(login=usuario_inativo.email, password="SenhaSegura123!")


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_authentication_signup_success(mock_tenant, db):
    mock_tenant.return_value = None
    auth = Authentication()
    user = auth.signup(
        username="unit_signup",
        email="unit_signup@example.com",
        password="SenhaSegura123!",
    )
    assert User.objects.filter(pk=user.pk).exists()
    mock_tenant.assert_called_once()


@pytest.mark.django_db
@patch("users.auth._create_tenant_db_for_user")
def test_authentication_signup_duplicate_raises(mock_tenant, usuario_comum):
    mock_tenant.return_value = None
    auth = Authentication()
    with pytest.raises(ValidationError):
        auth.signup(
            username=usuario_comum.username,
            email="email_novo_mas_username_dup@example.com",
            password="SenhaSegura123!",
        )
