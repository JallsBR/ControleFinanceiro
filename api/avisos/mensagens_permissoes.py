"""Regras de destinatários para mensagens internas (helpdesk, gerente, clientes)."""

from __future__ import annotations

from django.db.models import Q

from users.models import Consultoria, User


def user_e_helpdesk(u: User | None) -> bool:
    if u is None:
        return False
    return bool(getattr(u, "is_staff", False) or getattr(u, "is_superuser", False))


def pode_mensagem_entre(remetente: User, destino: User) -> bool:
    """
    Permite conversa entre:
    - helpdesk (staff ou superuser) e qualquer outro utilizador;
    - gerente e cliente com consultoria ativa (em qualquer direção).
    """
    if remetente is None or destino is None:
        return False
    if remetente.pk == destino.pk:
        return False
    if user_e_helpdesk(remetente) or user_e_helpdesk(destino):
        return True
    return Consultoria.objects.filter(
        status=Consultoria.Status.ATIVA,
    ).filter(
        Q(gerente_id=remetente.pk, cliente_id=destino.pk)
        | Q(gerente_id=destino.pk, cliente_id=remetente.pk)
    ).exists()


def destinatarios_permitidos_queryset(remetente: User):
    """
    Utilizadores que ``remetente`` pode escolher como destino de uma nova mensagem.
    Staff/superuser (helpdesk) pode endereçar qualquer conta para respostas de suporte.
    """
    if remetente is None:
        return User.objects.none()

    if user_e_helpdesk(remetente):
        return (
            User.objects.exclude(pk=remetente.pk)
            .order_by("-is_superuser", "-is_staff", "username")
            .distinct()
        )

    q_helpdesk = Q(is_staff=True) | Q(is_superuser=True)

    consultoria_ativa = Consultoria.objects.filter(status=Consultoria.Status.ATIVA)
    meus_gerentes = consultoria_ativa.filter(cliente_id=remetente.pk).values_list(
        "gerente_id", flat=True
    )
    meus_clientes = consultoria_ativa.filter(gerente_id=remetente.pk).values_list(
        "cliente_id", flat=True
    )

    return (
        User.objects.filter(q_helpdesk | Q(pk__in=meus_gerentes) | Q(pk__in=meus_clientes))
        .exclude(pk=remetente.pk)
        .order_by("-is_superuser", "-is_staff", "username")
        .distinct()
    )
