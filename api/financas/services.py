"""Regras de negócio da app finanças (agregações e relatórios)."""
from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal
from itertools import groupby
from typing import Any

from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear

from financas.models import Movimentacao
from financas.periodo_consolidado import months_in_closed_range

_DEC14 = DecimalField(max_digits=14, decimal_places=2)

_MESES_PT = (
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
)


def _label_mes_de_ano(ano: int, mes: int) -> str:
    if 1 <= mes <= 12:
        return f"{_MESES_PT[mes]} de {ano}"
    return f"Mês {mes} de {ano}"


def totais_movimentacoes_mes_civil(created_by, ano: int, mes: int) -> tuple[Decimal, Decimal]:
    """Soma entradas e saídas de todas as movimentações do mês civil (1 … último dia)."""
    d0 = date(ano, mes, 1)
    d1 = date(ano, mes, monthrange(ano, mes)[1])
    agg = Movimentacao.objects.filter(
        created_by=created_by, data__gte=d0, data__lte=d1
    ).aggregate(
        total_entradas=Coalesce(
            Sum(Case(When(tipo="E", then=F("valor")), output_field=_DEC14)),
            Value(Decimal("0")),
            output_field=_DEC14,
        ),
        total_saidas=Coalesce(
            Sum(Case(When(tipo="S", then=F("valor")), output_field=_DEC14)),
            Value(Decimal("0")),
            output_field=_DEC14,
        ),
    )
    te = agg["total_entradas"] if agg["total_entradas"] is not None else Decimal("0")
    ts = agg["total_saidas"] if agg["total_saidas"] is not None else Decimal("0")
    return te, ts


def consolidados_mensais_por_intervalo(created_by, d0: date, d1: date) -> list[dict]:
    """
    Um registo por mês civil que intersecta [d0, d1], com totais derivados de Movimentacao.
    Alinha com o que o utilizador vê nas movimentações (fonte única de verdade).
    """
    out: list[dict] = []
    for ano, mes in months_in_closed_range(d0, d1):
        te, ts = totais_movimentacoes_mes_civil(created_by, ano, mes)
        out.append(
            {
                "ano": ano,
                "mes": mes,
                "total_entradas": te,
                "total_saidas": ts,
            }
        )
    return out


def consolidados_mensais_todos_calculados(created_by) -> list[dict]:
    """Todos os meses civis que tenham pelo menos uma movimentação, mais recentes primeiro."""
    rows = (
        Movimentacao.objects.filter(created_by=created_by)
        .values(ano=ExtractYear("data"), mes=ExtractMonth("data"))
        .annotate(
            total_entradas=Coalesce(
                Sum(Case(When(tipo="E", then=F("valor")), output_field=_DEC14)),
                Value(Decimal("0")),
                output_field=_DEC14,
            ),
            total_saidas=Coalesce(
                Sum(Case(When(tipo="S", then=F("valor")), output_field=_DEC14)),
                Value(Decimal("0")),
                output_field=_DEC14,
            ),
        )
        .order_by("-ano", "-mes")
    )
    return list(rows)


def consolidados_mensais_ultimos_n(created_by, n: int = 12) -> list[dict]:
    """Até os últimos N meses (por data de calendário) que tenham movimentações."""
    return consolidados_mensais_todos_calculados(created_by)[: max(0, n)]


def linhas_pdf_movimentacoes_com_quebras_mes(
    movimentacoes_ordenadas: list[Any],
) -> list[dict[str, Any]]:
    """
    Monta a sequência de linhas da tabela do PDF: movimentações na ordem dada,
    com duas linhas extra entre meses distintos — subtotal do mês que fechou
    (apenas com base nas movimentações desta lista) e título do mês seguinte.
    Não altera totais globais do relatório (são linhas de apresentação).
    """
    if not movimentacoes_ordenadas:
        return []

    out: list[dict[str, Any]] = []
    grupos: list[tuple[tuple[int, int], list[Any]]] = []
    for k, g in groupby(
        movimentacoes_ordenadas,
        lambda m: (m.data.year, m.data.month),
    ):
        grupos.append((k, list(g)))

    for i, ((y_fechado, mon_fechado), rows) in enumerate(grupos):
        for m in rows:
            out.append({"tipo": "mov", "mov": m})
        if i >= len(grupos) - 1:
            break
        te = Decimal("0")
        ts = Decimal("0")
        for m in rows:
            v = m.valor if m.valor is not None else Decimal("0")
            if m.tipo == "E":
                te += v
            elif m.tipo == "S":
                ts += v
        saldo = te - ts
        y_prox, mon_prox = grupos[i + 1][0]
        out.append(
            {
                "tipo": "subtotal_mes",
                "mes_fechado_label": _label_mes_de_ano(y_fechado, mon_fechado),
                "total_entradas": te,
                "total_saidas": ts,
                "saldo": saldo,
            }
        )
        out.append(
            {
                "tipo": "titulo_mes",
                "titulo": _label_mes_de_ano(y_prox, mon_prox),
            }
        )
    return out
