from __future__ import annotations

import secrets
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import APIException, AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from integrations.email.services import enviar_otp_login, enviar_redefinicao_senha
from users.auth import Authentication
from users.models import (
    AceiteTermoUso,
    PasswordResetChallenge,
    TermoUso,
    TwoFactorChallenge,
    User,
)
from users.serializers import UserSerializer

if TYPE_CHECKING:
    from django.http import HttpRequest

OTP_LENGTH = 6
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def obter_termo_vigente() -> TermoUso | None:
    return (
        TermoUso.objects.filter(ativo=True)
        .order_by("-vigente_desde", "-id")
        .first()
    )


def validar_aceite_termo(termo_versao: str | None, termo_aceite: bool | None) -> TermoUso:
    if not termo_aceite:
        raise ValidationError(
            {"termo_aceite": "É necessário aceitar o Termo de Uso vigente para criar uma conta."}
        )

    if not termo_versao or not str(termo_versao).strip():
        raise ValidationError(
            {"termo_versao": "Informe a versão do Termo de Uso que você está aceitando."}
        )

    termo = obter_termo_vigente()
    if termo is None:
        raise ValidationError(
            {"detail": "Nenhum Termo de Uso está publicado no momento. Tente novamente mais tarde."}
        )

    if termo.version != str(termo_versao).strip():
        raise ValidationError(
            {
                "termo_versao": (
                    "A versão do Termo de Uso não corresponde à vigente. "
                    "Recarregue a página e leia o documento atualizado."
                )
            }
        )

    return termo


def _extrair_metadados_requisicao(request: HttpRequest | None) -> tuple[str | None, str]:
    if request is None:
        return None, ""
    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
    return ip, user_agent


def registrar_aceite_termo(
    user: User,
    termo: TermoUso,
    *,
    request: HttpRequest | None = None,
) -> AceiteTermoUso:
    ip, user_agent = _extrair_metadados_requisicao(request)
    return AceiteTermoUso.objects.create(
        user=user,
        termo=termo,
        ip_address=ip,
        user_agent=user_agent,
    )


def cadastrar_usuario(
    *,
    username: str,
    email: str,
    password: str,
    termo_versao: str | None,
    termo_aceite: bool | None,
    request: HttpRequest | None = None,
) -> User:
    termo = validar_aceite_termo(termo_versao, termo_aceite)
    auth = Authentication()
    user = auth.signup(username=username, email=email, password=password)
    registrar_aceite_termo(user, termo, request=request)
    return user


def publicar_termo_inicial() -> None:
    """Cria a versão 1.0.0 se ainda não existir (migration / comando)."""
    from users.legal.termo_uso_v1 import CONTEUDO, TITULO, VERSAO

    if TermoUso.objects.filter(version=VERSAO).exists():
        return

    agora = timezone.now()
    TermoUso.objects.filter(ativo=True).update(ativo=False)
    TermoUso.objects.create(
        version=VERSAO,
        titulo=TITULO,
        conteudo=CONTEUDO,
        vigente_desde=agora,
        ativo=True,
    )


def _gerar_otp_numerico() -> str:
    upper = 10**OTP_LENGTH
    return str(secrets.randbelow(upper)).zfill(OTP_LENGTH)


def _tokens_para_usuario(user: User) -> dict[str, Any]:
    token = RefreshToken.for_user(user)
    return {
        "user": UserSerializer(user).data,
        "refresh": str(token),
        "access": str(token.access_token),
    }


def _invalidar_desafios_abertos(user: User) -> None:
    agora = timezone.now()
    TwoFactorChallenge.objects.filter(
        user=user,
        consumed_at__isnull=True,
        expires_at__gt=agora,
    ).update(consumed_at=agora)


@transaction.atomic
def _criar_desafio_e_enviar_otp(user: User) -> TwoFactorChallenge:
    _invalidar_desafios_abertos(user)
    codigo = _gerar_otp_numerico()
    link_token = secrets.token_urlsafe(32)
    desafio = TwoFactorChallenge.objects.create(
        user=user,
        code_hash=make_password(codigo),
        link_token_hash=make_password(link_token),
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    magic_url = (
        f"{settings.FRONTEND_URL}/auth/2fa-link"
        f"?c={desafio.id}&t={link_token}"
    )
    try:
        enviar_otp_login(user, codigo, magic_url)
    except Exception as exc:
        raise APIException(
            "Não foi possível enviar o e-mail de verificação. "
            "Confira a configuração SMTP e tente novamente."
        ) from exc
    return desafio


def autenticar_signin(*, login: str, password: str) -> dict[str, Any]:
    """
    Valida credenciais. Se 2FA estiver desligado, devolve JWT.
    Se ligado, cria desafio OTP e devolve requires_2fa + challenge_id (sem tokens).
    """
    auth = Authentication()
    user = auth.signin(login=login, password=password)

    if not user.two_factor_enabled:
        return _tokens_para_usuario(user)

    desafio = _criar_desafio_e_enviar_otp(user)
    return {
        "requires_2fa": True,
        "challenge_id": str(desafio.id),
    }


def verificar_otp_login(
    *,
    challenge_id: str,
    code: str | None = None,
    link_token: str | None = None,
) -> dict[str, Any]:
    """Valida OTP numérico ou link mágico e devolve JWT + user."""
    exception_auth = AuthenticationFailed("Código inválido ou expirado.")
    code_limpo = (code or "").strip()
    link_limpo = (link_token or "").strip()

    usa_codigo = bool(code_limpo)
    usa_link = bool(link_limpo)
    if usa_codigo == usa_link:
        # Exatamente um dos dois deve ser informado
        raise exception_auth

    if usa_codigo and (len(code_limpo) != OTP_LENGTH or not code_limpo.isdigit()):
        raise exception_auth

    try:
        cid = UUID(str(challenge_id).strip())
    except (TypeError, ValueError):
        raise exception_auth from None

    falhou = False
    resultado: dict[str, Any] | None = None

    with transaction.atomic():
        try:
            desafio = (
                TwoFactorChallenge.objects.select_for_update()
                .select_related("user")
                .get(pk=cid)
            )
        except TwoFactorChallenge.DoesNotExist as exc:
            raise exception_auth from exc

        agora = timezone.now()
        if desafio.consumed_at is not None or desafio.expires_at <= agora:
            raise exception_auth

        if desafio.attempts >= OTP_MAX_ATTEMPTS:
            if desafio.consumed_at is None:
                desafio.consumed_at = agora
                desafio.save(update_fields=["consumed_at"])
            falhou = True
        else:
            valido = False
            if usa_codigo:
                valido = check_password(code_limpo, desafio.code_hash)
            elif desafio.link_token_hash:
                valido = check_password(link_limpo, desafio.link_token_hash)

            if not valido:
                desafio.attempts += 1
                updates = ["attempts"]
                if desafio.attempts >= OTP_MAX_ATTEMPTS:
                    desafio.consumed_at = agora
                    updates.append("consumed_at")
                desafio.save(update_fields=updates)
                falhou = True
            elif not desafio.user.is_active:
                raise exception_auth
            else:
                desafio.consumed_at = agora
                desafio.save(update_fields=["consumed_at"])
                resultado = _tokens_para_usuario(desafio.user)

    if falhou or resultado is None:
        raise exception_auth
    return resultado


PASSWORD_RESET_TTL_MINUTES = 30
PASSWORD_RESET_GENERIC_MSG = (
    "Se existir uma conta com esses dados, enviamos um e-mail com instruções "
    "para redefinir a senha."
)


def _invalidar_resets_abertos(user: User) -> None:
    agora = timezone.now()
    PasswordResetChallenge.objects.filter(
        user=user,
        consumed_at__isnull=True,
        expires_at__gt=agora,
    ).update(consumed_at=agora)


def solicitar_redefinicao_senha(*, login: str) -> dict[str, str]:
    """
    Dispara e-mail de reset se o utilizador existir e estiver ativo.
    Sempre devolve a mesma mensagem (anti-enumeração).
    """
    login = (login or "").strip()
    if not login:
        raise ValidationError({"login": "Informe o e-mail ou nome de usuário."})

    user = (
        User.objects.filter(Q(email__iexact=login) | Q(username__iexact=login))
        .filter(is_active=True)
        .first()
    )
    if user is None:
        return {"detail": PASSWORD_RESET_GENERIC_MSG}

    token = secrets.token_urlsafe(32)
    with transaction.atomic():
        _invalidar_resets_abertos(user)
        desafio = PasswordResetChallenge.objects.create(
            user=user,
            token_hash=make_password(token),
            expires_at=timezone.now()
            + timedelta(minutes=PASSWORD_RESET_TTL_MINUTES),
        )
        reset_url = (
            f"{settings.FRONTEND_URL}/auth/redefinir-senha"
            f"?c={desafio.id}&t={token}"
        )
        try:
            enviar_redefinicao_senha(
                user,
                reset_url,
                minutos=PASSWORD_RESET_TTL_MINUTES,
            )
        except Exception as exc:
            raise APIException(
                "Não foi possível enviar o e-mail de redefinição. "
                "Confira a configuração SMTP e tente novamente."
            ) from exc

    return {"detail": PASSWORD_RESET_GENERIC_MSG}


def confirmar_redefinicao_senha(
    *,
    challenge_id: str,
    token: str,
    new_password: str,
) -> dict[str, str]:
    """Valida o link e define a nova senha."""
    exception_auth = AuthenticationFailed("Link inválido ou expirado.")
    token = (token or "").strip()
    new_password = new_password or ""
    if not token or not new_password:
        raise exception_auth

    try:
        cid = UUID(str(challenge_id).strip())
    except (TypeError, ValueError):
        raise exception_auth from None

    with transaction.atomic():
        try:
            desafio = (
                PasswordResetChallenge.objects.select_for_update()
                .select_related("user")
                .get(pk=cid)
            )
        except PasswordResetChallenge.DoesNotExist as exc:
            raise exception_auth from exc

        agora = timezone.now()
        if desafio.consumed_at is not None or desafio.expires_at <= agora:
            raise exception_auth

        if not check_password(token, desafio.token_hash):
            raise exception_auth

        user = desafio.user
        if not user.is_active:
            raise exception_auth

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            raise ValidationError({"new_password": list(exc.messages)}) from exc

        user.set_password(new_password)
        user.save(update_fields=["password"])
        desafio.consumed_at = agora
        desafio.save(update_fields=["consumed_at"])
        _invalidar_resets_abertos(user)

    return {"detail": "Senha redefinida com sucesso. Você já pode entrar."}
