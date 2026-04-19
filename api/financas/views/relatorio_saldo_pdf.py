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
from financas.models import Categoria, ConsolidadoMensal, Movimentacao

def _inter_font_face_css() -> str:
    """Carrega Inter a partir de ficheiros em static (sem pedidos a fonts.googleapis.com)."""
    fonts_dir = (
        Path(__file__).resolve().parent.parent / "static" / "financas" / "fonts"
    )
    chunks: list[str] = []
    for weight, filename in (
        (400, "Inter-Regular.ttf"),
        (500, "Inter-Medium.ttf"),
        (600, "Inter-SemiBold.ttf"),
        (700, "Inter-Bold.ttf"),
    ):
        path = fonts_dir / filename
        if not path.is_file():
            continue
        uri = path.resolve().as_uri()
        # str.format: chaves do bloco CSS têm de ser {{ }} senão {font-family…} vira KeyError.
        chunks.append(
            (
                "@font-face{{font-family:Inter;font-style:normal;font-weight:{weight};"
                "font-display:swap;src:url('{uri}') format('truetype');}}"
            ).format(weight=weight, uri=uri)
        )
    return "".join(chunks)


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


def _parse_categorias_ids(raw: str | None) -> list[int]:
    if not raw or not str(raw).strip():
        return []
    out: list[int] = []
    for part in str(raw).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            continue
    return out


def _filtros_resumo_texto(
    user,
    tipo: str | None,
    categorias_ids: list[int],
    descricao: str | None,
) -> str:
    partes: list[str] = []
    if tipo == "E":
        partes.append("Tipo: Entrada")
    elif tipo == "S":
        partes.append("Tipo: Saída")
    if categorias_ids:
        nomes = list(
            Categoria.objects.filter(created_by=user, id__in=categorias_ids)
            .values_list("nome", flat=True)
            .order_by("nome")
        )
        if nomes:
            partes.append("Categorias: " + ", ".join(nomes))
    if descricao:
        partes.append(f'Descrição contém: "{descricao}"')
    return " · ".join(partes)


class RelatorioSaldoPdfView(APIView):
    """
    GET ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD
    Opcional (alinhado com o filtro da tabela no front):
    - tipo=E|S
    - categorias=1,2,3 (ids de categoria)
    - descricao=... (contém, sem distinção de maiúsculas)

    Gera PDF com resumo do período (sobre as movimentações filtradas),
    movimentações filtradas e consolidados mensais globais do utilizador.
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

        tipo_raw = (request.query_params.get("tipo") or "").strip().upper()
        tipo_filtro = tipo_raw if tipo_raw in ("E", "S") else None
        categorias_ids = _parse_categorias_ids(request.query_params.get("categorias"))
        descricao_filtro = (request.query_params.get("descricao") or "").strip() or None

        user = get_financas_subject_user(request)
        movs_qs = (
            Movimentacao.objects.filter(created_by=user, data__gte=d0, data__lte=d1)
            .select_related("categoria")
            .order_by("data", "id")
        )
        if tipo_filtro:
            movs_qs = movs_qs.filter(tipo=tipo_filtro)
        if categorias_ids:
            movs_qs = movs_qs.filter(categoria_id__in=categorias_ids)
        if descricao_filtro:
            movs_qs = movs_qs.filter(descricao__icontains=descricao_filtro)

        movimentacoes = list(movs_qs)

        filtros_resumo = _filtros_resumo_texto(
            user, tipo_filtro, categorias_ids, descricao_filtro
        )

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
                "inter_font_face_css": _inter_font_face_css(),
                "data_inicio": d0,
                "data_fim": d1,
                "filtros_resumo": filtros_resumo,
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
