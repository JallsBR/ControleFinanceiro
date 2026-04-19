"""Helpers para filtrar consolidados mensais por intervalo de datas (calendário)."""
from __future__ import annotations

from datetime import date
from functools import reduce
import operator

from django.db.models import Q


def months_in_closed_range(d0: date, d1: date) -> list[tuple[int, int]]:
    """
    Meses civis (ano, mês) que intersectam [d0, d1], inclusive.
    Ex.: 2025-01-15 a 2025-03-10 → janeiro, fevereiro e março de 2025.
    """
    if d0 > d1:
        return []
    out: list[tuple[int, int]] = []
    y, m = d0.year, d0.month
    while (y, m) <= (d1.year, d1.month):
        out.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def consolidado_q_por_intervalo(d0: date, d1: date) -> Q:
    """Q para filtrar ConsolidadoMensal pelo intervalo; sem resultados se intervalo vazio."""
    pairs = months_in_closed_range(d0, d1)
    if not pairs:
        return Q(pk__in=[])
    return reduce(operator.or_, (Q(ano=y, mes=m) for y, m in pairs))
