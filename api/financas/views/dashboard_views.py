from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Max, Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from financas.models import (
    ConsolidadoMensal,
    Movimentacao,
    Meta,
    Investimento,
    Reserva,
)


class DashboardView(generics.GenericAPIView):
    """
    View usada para alimentar o dashboard da home do front.

    Retorna um JSON no formato:
    {
        entradas: 1000,      # soma das entradas do mês corrente
        saidas: 500,         # soma das saídas do mês corrente
        saldo: 500,          # entradas - saídas do mês corrente
        reservas: 1000,      # soma de todas as reservas ativas
        consolidado: 5000,   # saldo consolidado do mês anterior
        ultimos7dias: 1000,  # soma das saídas dos últimos 7 dias
        ultimos30dias: 2000, # soma das saídas dos últimos 30 dias
        maior_saida: 1000,   # maior saída do mês corrente
        investimentos: 1000, # soma de todos os investimentos ativos
        meta_geral: 1000,    # soma de todas as metas em aberto
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now().date()
        ano_atual = today.year
        mes_atual = today.month

        # Movimentações do usuário
        movs_usuario = Movimentacao.objects.filter(created_by=user)
        movs_mes_atual = movs_usuario.filter(
            data__year=ano_atual,
            data__month=mes_atual,
        )

        # Entradas e saídas do mês corrente
        entradas = movs_mes_atual.filter(tipo="E").aggregate(
            total=Sum("valor")
        )["total"] or Decimal("0")

        saidas = movs_mes_atual.filter(tipo="S").aggregate(
            total=Sum("valor")
        )["total"] or Decimal("0")

        saldo = entradas - saidas

        # Reservas ativas
        reservas = (
            Reserva.objects.filter(created_by=user, ativa=True).aggregate(
                total=Sum("valor")
            )["total"]
            or Decimal("0")
        )

        # Consolidado do mês anterior
        if mes_atual == 1:
            mes_anterior = 12
            ano_anterior = ano_atual - 1
        else:
            mes_anterior = mes_atual - 1
            ano_anterior = ano_atual

        consolidado_obj = ConsolidadoMensal.objects.filter(
            created_by=user,
            ano=ano_anterior,
            mes=mes_anterior,
        ).first()

        if consolidado_obj:
            consolidado = (
                consolidado_obj.total_entradas - consolidado_obj.total_saidas
            )
        else:
            consolidado = Decimal("0")

        # Saídas dos últimos 7 e 30 dias
        sete_dias_atras = today - timedelta(days=7)
        trinta_dias_atras = today - timedelta(days=30)

        ultimos7dias = (
            movs_usuario.filter(
                tipo="S",
                data__gte=sete_dias_atras,
                data__lte=today,
            ).aggregate(total=Sum("valor"))["total"]
            or Decimal("0")
        )

        ultimos30dias = (
            movs_usuario.filter(
                tipo="S",
                data__gte=trinta_dias_atras,
                data__lte=today,
            ).aggregate(total=Sum("valor"))["total"]
            or Decimal("0")
        )

        # Maior saída do mês corrente (valor e descrição)
        maior_movimentacao_saida = (
            movs_mes_atual.filter(tipo="S")
            .order_by("-valor")
            .first()
        )

        if maior_movimentacao_saida:
            maior_saida = maior_movimentacao_saida.valor
            descricao_maior_saida = (
                (maior_movimentacao_saida.descricao or "").strip()
                or maior_movimentacao_saida.categoria.nome
            )
        else:
            maior_saida = Decimal("0")
            descricao_maior_saida = ""

        # Soma de investimentos (ativos) do usuário
        investimentos = (
            Investimento.objects.filter(
                Q(usuario=user) | Q(created_by=user),
                ativo=True,
            ).aggregate(total=Sum("valor_inicial"))["total"]
            or Decimal("0")
        )

        # Soma de todas as metas em aberto (não concluídas)
        meta_geral = (
            Meta.objects.filter(created_by=user, concluida=False).aggregate(
                total=Sum("valor_meta")
            )["total"]
            or Decimal("0")
        )

        data = {
            "entradas": entradas,
            "saidas": saidas,
            "saldo": saldo,
            "reservas": reservas,
            "consolidado": consolidado,
            "ultimos7dias": ultimos7dias,
            "ultimos30dias": ultimos30dias,
            "maior_saida": maior_saida,
            "descricao_maior_saida": descricao_maior_saida,
            "investimentos": investimentos,
            "meta_geral": meta_geral,
        }

        return Response(data)