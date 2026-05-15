"""API /api/v1/financas/movimentacoes/ — lista, CRUD e filtro (requisitos tipo 1 + 7 + 8)."""

from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Movimentacao


@pytest.mark.django_db
def test_get_movimentacao_list_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("movimentacao-list-create"))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_movimentacao_list_forbidden_subject_header(
    client_autenticado_comum, outro_usuario_comum
):
    resp = client_autenticado_comum.get(
        reverse("movimentacao-list-create"),
        HTTP_X_FINANCAS_SUBJECT_USER=str(outro_usuario_comum.pk),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_movimentacao_list_success(client_autenticado_comum, usuario_comum):
    today = timezone.now().date()
    cat = Categoria.objects.filter(created_by=usuario_comum, tipo="E").first()
    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("50.00"),
        data=today,
        categoria=cat,
        descricao="mov teste lista",
        created_by=usuario_comum,
    )
    resp = client_autenticado_comum.get(reverse("movimentacao-list-create"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "results" in body
    descricoes = {r.get("descricao", "") for r in body["results"]}
    assert "mov teste lista" in descricoes


@pytest.mark.django_db
def test_get_movimentacao_list_scope_isolation(
    client_autenticado_comum, usuario_comum, outro_usuario_comum
):
    today = timezone.now().date()
    cat_outro = Categoria.objects.filter(created_by=outro_usuario_comum, tipo="S").first()
    Movimentacao.objects.create(
        tipo="S",
        valor=Decimal("77.00"),
        data=today,
        categoria=cat_outro,
        descricao="SECRET_OUTRO_USER",
        created_by=outro_usuario_comum,
    )
    resp = client_autenticado_comum.get(reverse("movimentacao-list-create"))
    descricoes = {r.get("descricao", "") for r in resp.json()["results"]}
    assert "SECRET_OUTRO_USER" not in descricoes


@pytest.mark.django_db
def test_get_movimentacao_list_filter_data_gte(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.filter(created_by=usuario_comum, tipo="E").first()
    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("1.00"),
        data=date(2020, 1, 15),
        categoria=cat,
        descricao="antiga",
        created_by=usuario_comum,
    )
    Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("2.00"),
        data=date(2030, 6, 1),
        categoria=cat,
        descricao="futura",
        created_by=usuario_comum,
    )
    resp = client_autenticado_comum.get(
        reverse("movimentacao-list-create"),
        {"data__gte": "2030-01-01"},
    )
    assert resp.status_code == status.HTTP_200_OK
    descricoes = {r["descricao"] for r in resp.json()["results"]}
    assert "futura" in descricoes
    assert "antiga" not in descricoes


@pytest.mark.django_db
def test_post_movimentacao_create_unauthenticated():
    client = APIClient()
    resp = client.post(
        reverse("movimentacao-list-create"),
        {"tipo": "E", "valor": "10.00", "data": "2025-01-01", "categoria": 1},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_movimentacao_create_validation_required(client_autenticado_comum):
    resp = client_autenticado_comum.post(
        reverse("movimentacao-list-create"), {"tipo": "E"}, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_post_movimentacao_create_success(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.filter(created_by=usuario_comum, tipo="S").first()
    today = timezone.now().date().isoformat()
    resp = client_autenticado_comum.post(
        reverse("movimentacao-list-create"),
        {
            "tipo": "S",
            "valor": "33.50",
            "data": today,
            "categoria": cat.pk,
            "descricao": "compra teste",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert Movimentacao.objects.filter(
        descricao="compra teste", created_by=usuario_comum
    ).exists()


@pytest.mark.django_db
def test_get_movimentacao_detail_not_found(client_autenticado_comum):
    resp = client_autenticado_comum.get(
        reverse("movimentacao-retrieve-update-destroy", kwargs={"pk": 999_999})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_movimentacao_detail_scope_isolation(
    client_autenticado_comum, outro_usuario_comum
):
    today = timezone.now().date()
    cat = Categoria.objects.filter(created_by=outro_usuario_comum, tipo="E").first()
    mov = Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("5.00"),
        data=today,
        categoria=cat,
        created_by=outro_usuario_comum,
    )
    resp = client_autenticado_comum.get(
        reverse("movimentacao-retrieve-update-destroy", kwargs={"pk": mov.pk})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_movimentacao_success(client_autenticado_comum, usuario_comum):
    today = timezone.now().date()
    cat = Categoria.objects.filter(created_by=usuario_comum, tipo="E").first()
    mov = Movimentacao.objects.create(
        tipo="E",
        valor=Decimal("1.00"),
        data=today,
        categoria=cat,
        created_by=usuario_comum,
    )
    pk = mov.pk
    resp = client_autenticado_comum.delete(
        reverse("movimentacao-retrieve-update-destroy", kwargs={"pk": pk})
    )
    assert resp.status_code == status.HTTP_200_OK
    assert not Movimentacao.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_delete_movimentacao_scope_isolation(
    client_autenticado_comum, outro_usuario_comum, usuario_comum
):
    today = timezone.now().date()
    cat = Categoria.objects.filter(created_by=outro_usuario_comum, tipo="S").first()
    mov = Movimentacao.objects.create(
        tipo="S",
        valor=Decimal("9.00"),
        data=today,
        categoria=cat,
        created_by=outro_usuario_comum,
    )
    resp = client_autenticado_comum.delete(
        reverse("movimentacao-retrieve-update-destroy", kwargs={"pk": mov.pk})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert Movimentacao.objects.filter(pk=mov.pk).exists()
