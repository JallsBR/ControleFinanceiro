"""GET /api/v1/financas/dashboard/ — tipo 3 (agregados) com valores conferidos ao ORM."""

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Movimentacao


@pytest.mark.django_db
def test_get_aggregate_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_aggregate_success(client_autenticado_comum, usuario_comum):
    Movimentacao.objects.filter(created_by=usuario_comum).delete()
    today = timezone.now().date()
    cat_e = Categoria.objects.filter(created_by=usuario_comum, tipo="E").first()
    cat_s = Categoria.objects.filter(created_by=usuario_comum, tipo="S").first()
    assert cat_e is not None and cat_s is not None

    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("100.00"),
        data=today,
        categoria=cat_e,
        created_by=usuario_comum,
    )
    Movimentacao.objects.create(
        tipo="S",
        valor=Decimal("40.00"),
        data=today,
        categoria=cat_s,
        created_by=usuario_comum,
    )

    resp = client_autenticado_comum.get(reverse("dashboard"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert Decimal(str(body["entradas"])) == Decimal("100")
    assert Decimal(str(body["saidas"])) == Decimal("40")
    assert Decimal(str(body["saldo"])) == Decimal("60")


@pytest.mark.django_db
def test_get_aggregate_scope_isolation(
    client_autenticado_comum, usuario_comum, outro_usuario_comum
):
    """Movimentação de outro utilizador não entra nos agregados do subject."""
    Movimentacao.objects.filter(
        created_by__in=[usuario_comum.pk, outro_usuario_comum.pk]
    ).delete()
    today = timezone.now().date()
    cat_e = Categoria.objects.filter(created_by=usuario_comum, tipo="E").first()
    cat_e_outro = Categoria.objects.filter(created_by=outro_usuario_comum, tipo="E").first()
    assert cat_e is not None and cat_e_outro is not None

    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("999.00"),
        data=today,
        categoria=cat_e_outro,
        created_by=outro_usuario_comum,
    )
    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("10.00"),
        data=today,
        categoria=cat_e,
        created_by=usuario_comum,
    )

    resp = client_autenticado_comum.get(reverse("dashboard"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert Decimal(str(body["entradas"])) == Decimal("10")
