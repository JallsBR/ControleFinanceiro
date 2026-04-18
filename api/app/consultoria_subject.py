"""Regras de permissão para solicitações/consultoria com ``X-Financas-Subject-User`` (staff)."""

from __future__ import annotations

from django.http import HttpRequest

from app.financas_subject import get_financas_subject_user


def request_user_pode_atuar_como_consultor_da_solicitacao(
    request: HttpRequest, consultor_id_solicitacao: int
) -> bool:
    """
    O consultor real (JWT) ou staff a visualizar esse consultor (subject = gerente)
    pode aceitar/recusar/encerrar pedidos em que ``consultor_id`` coincide.
    """
    user = request.user
    if not getattr(user, "is_authenticated", False):
        return False
    if consultor_id_solicitacao == user.id:
        return True
    if not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
        return False
    subject = get_financas_subject_user(request)
    if not subject or subject.id == user.id:
        return False
    return bool(
        getattr(subject, "is_gerente", False)
        and consultor_id_solicitacao == subject.id
    )
