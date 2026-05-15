"""GET /api/v1/financas/relatorios/saldo.pdf — tipo 4 (download PDF)."""

from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Movimentacao


@pytest.mark.django_db
def test_get_download_unauthenticated():
    client = APIClient()
    resp = client.get(
        reverse("financas-relatorio-saldo-pdf"),
        {"data_inicio": "2025-01-01", "data_fim": "2025-01-31"},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_download_forbidden_subject_header(
    client_autenticado_comum, outro_usuario_comum
):
    resp = client_autenticado_comum.get(
        reverse("financas-relatorio-saldo-pdf"),
        {"data_inicio": "2025-01-01", "data_fim": "2025-01-31"},
        HTTP_X_FINANCAS_SUBJECT_USER=str(outro_usuario_comum.pk),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_download_bad_request_missing_dates(client_autenticado_comum):
    resp = client_autenticado_comum.get(reverse("financas-relatorio-saldo-pdf"))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_inicio" in resp.json().get("detail", "").lower()


@pytest.mark.django_db
def test_get_download_stream_success(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.filter(created_by=usuario_comum, tipo="E").first()
    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("15.00"),
        data=date(2025, 1, 10),
        categoria=cat,
        created_by=usuario_comum,
    )
    resp = client_autenticado_comum.get(
        reverse("financas-relatorio-saldo-pdf"),
        {"data_inicio": "2025-01-01", "data_fim": "2025-01-31"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp["Content-Type"] == "application/pdf"
    assert "attachment" in resp["Content-Disposition"].lower()
    assert len(resp.content) > 100
    assert resp.content[:4] == b"%PDF"


@pytest.mark.django_db
def test_get_download_scope_isolation_pdf_bytes(
    client_autenticado_comum, usuario_comum, outro_usuario_comum
):
    """Dados do outro utilizador não devem aparecer como texto no PDF gerado para o subject."""
    cat_outro = Categoria.objects.filter(created_by=outro_usuario_comum, tipo="E").first()
    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("1.00"),
        data=date(2025, 1, 5),
        categoria=cat_outro,
        descricao="MARCA_ISOLAMENTO_PDF_OUTRO",
        created_by=outro_usuario_comum,
    )
    resp = client_autenticado_comum.get(
        reverse("financas-relatorio-saldo-pdf"),
        {"data_inicio": "2025-01-01", "data_fim": "2025-01-31"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert b"MARCA_ISOLAMENTO_PDF_OUTRO" not in resp.content
