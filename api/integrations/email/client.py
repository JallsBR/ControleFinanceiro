"""Cliente de e-mail via Django (SMTP / console)."""

from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail


def send_plain_email(
    *,
    subject: str,
    message: str,
    recipient_list: list[str],
    from_email: str | None = None,
) -> int:
    """Envia e-mail de texto puro. Retorna a quantidade enviada."""
    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


def send_html_email(
    *,
    subject: str,
    text_body: str,
    html_body: str,
    recipient_list: list[str],
    from_email: str | None = None,
) -> int:
    """Envia e-mail multipart (texto + HTML)."""
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    msg.attach_alternative(html_body, "text/html")
    return msg.send(fail_silently=False)
