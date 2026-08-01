"""Serviços de domínio para e-mails transacionais (OTP, etc.)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.template.loader import render_to_string

from integrations.email.client import send_html_email

if TYPE_CHECKING:
    from users.models import User


def enviar_otp_login(user: User, codigo_plain: str, magic_url: str) -> None:
    """
    Envia o código OTP + link mágico ao e-mail cadastrado.
    Código e token do link em claro só circulam nesta chamada — não logar.
    """
    nome = (user.first_name or user.username or "").strip() or "usuário"
    minutos = 10
    from_email = settings.DEFAULT_FROM_EMAIL
    subject = "Código de verificação — Finanças APP"
    text_body = (
        f"Olá, {nome}.\n\n"
        f"Seu código de autenticação em dois fatores é: {codigo_plain}\n\n"
        f"Ou entre direto por este link (válido por {minutos} minutos):\n"
        f"{magic_url}\n\n"
        "Se você não tentou entrar na conta, ignore este e-mail e altere sua senha.\n\n"
        "— Finanças APP\n"
    )
    html_body = render_to_string(
        "users/email/otp_login.html",
        {
            "nome": nome,
            "codigo": codigo_plain,
            "magic_url": magic_url,
            "minutos": minutos,
            "from_email": from_email,
        },
    )
    send_html_email(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        recipient_list=[user.email],
    )


def enviar_redefinicao_senha(user: User, reset_url: str, *, minutos: int = 30) -> None:
    """Envia o link de redefinição de senha. Não logar o token/URL completo."""
    nome = (user.first_name or user.username or "").strip() or "usuário"
    from_email = settings.DEFAULT_FROM_EMAIL
    subject = "Redefinir senha — Finanças APP"
    text_body = (
        f"Olá, {nome}.\n\n"
        f"Recebemos um pedido para redefinir a senha da sua conta.\n"
        f"Abra este link (válido por {minutos} minutos):\n"
        f"{reset_url}\n\n"
        "Se você não pediu isso, ignore este e-mail — sua senha permanece a mesma.\n\n"
        "— Finanças APP\n"
    )
    html_body = render_to_string(
        "users/email/password_reset.html",
        {
            "nome": nome,
            "reset_url": reset_url,
            "minutos": minutos,
            "from_email": from_email,
        },
    )
    send_html_email(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        recipient_list=[user.email],
    )
