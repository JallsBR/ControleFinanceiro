from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from app.financas_subject import get_financas_subject_user
from financas.models import ConsolidadoMensal, Movimentacao

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


class RelatorioSaldoPdfView(APIView):
    """
    GET ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD
    Gera PDF com resumo do período, movimentações e consolidados mensais
    (mesmo utilizador sujeito que /financas/movimentacoes/).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        di = request.query_params.get("data_inicio")
        df = request.query_params.get("data_fim")
        if not di or not df:
            return Response(
                {
                    "detail": "Parâmetros data_inicio e data_fim são obrigatórios (YYYY-MM-DD).",
                },
                status=400,
            )
        try:
            d0 = datetime.strptime(di.strip(), "%Y-%m-%d").date()
            d1 = datetime.strptime(df.strip(), "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Datas inválidas. Use o formato YYYY-MM-DD."},
                status=400,
            )
        if d0 > d1:
            return Response(
                {"detail": "data_inicio não pode ser posterior a data_fim."},
                status=400,
            )

        user = get_financas_subject_user(request)
        movs_qs = (
            Movimentacao.objects.filter(created_by=user, data__gte=d0, data__lte=d1)
            .select_related("categoria")
            .order_by("data", "id")
        )
        movimentacoes = list(movs_qs)

        total_entradas = Decimal("0")
        total_saidas = Decimal("0")
        for m in movimentacoes:
            v = m.valor or Decimal("0")
            if m.tipo == "E":
                total_entradas += v
            elif m.tipo == "S":
                total_saidas += v
        saldo_periodo = total_entradas - total_saidas

        consolidados_qs = ConsolidadoMensal.objects.filter(created_by=user).order_by(
            "-ano", "-mes"
        )
        consolidados_linhas = []
        for c in consolidados_qs:
            te = c.total_entradas or Decimal("0")
            ts = c.total_saidas or Decimal("0")
            m = int(c.mes)
            if 1 <= m <= 12:
                periodo_label = f"{_MESES_PT[m]} - {c.ano}"
            else:
                periodo_label = f"{c.mes} - {c.ano}"
            consolidados_linhas.append(
                {
                    "ano": c.ano,
                    "mes": c.mes,
                    "periodo_label": periodo_label,
                    "total_entradas": te,
                    "total_saidas": ts,
                    "saldo_mes": te - ts,
                }
            )

        # Nome no cabeçalho: dono dos dados (subject), não o staff/consultor autenticado.
        fn = (getattr(user, "first_name", None) or "").strip()
        ln = (getattr(user, "last_name", None) or "").strip()
        if fn or ln:
            nome_utilizador = f"{fn} {ln}".strip()
        else:
            nome_utilizador = user.get_username()

        logo_path = (
            Path(settings.BASE_DIR).parent
            / "front"
            / "src"
            / "assets"
            / "logoFinancasApp.png"
        )
        logo_uri = logo_path.resolve().as_uri() if logo_path.is_file() else ""

        html = render_to_string(
            "financas/relatorio_saldo.html",
            {
                "nome_utilizador": nome_utilizador,
                "logo_uri": logo_uri,
                "data_inicio": d0,
                "data_fim": d1,
                "movimentacoes": movimentacoes,
                "total_entradas": total_entradas,
                "total_saidas": total_saidas,
                "saldo_periodo": saldo_periodo,
                "consolidados_linhas": consolidados_linhas,
            },
            request=request,
        )

        base_url = request.build_absolute_uri("/")
        pdf_bytes = HTML(string=html, base_url=base_url).write_pdf()

        filename = f"saldo-{d0.isoformat()}_{d1.isoformat()}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
