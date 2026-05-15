from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from users.auth import Authentication
from users.models import AceiteTermoUso, TermoUso

if TYPE_CHECKING:
    from django.http import HttpRequest

    from users.models import User


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
