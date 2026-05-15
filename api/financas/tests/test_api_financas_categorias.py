"""API /api/v1/financas/categorias/ — tipos 1 (lista), 2 (detail), 7 (CRUD), 8 (delete)."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria


@pytest.mark.django_db
def test_get_list_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("categoria-list-create"))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_list_forbidden_subject_header_nao_gerente(
    client_autenticado_comum, outro_usuario_comum
):
    """Utilizador comum não pode usar X-Financas-Subject-User (403 no middleware)."""
    resp = client_autenticado_comum.get(
        reverse("categoria-list-create"),
        HTTP_X_FINANCAS_SUBJECT_USER=str(outro_usuario_comum.pk),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert "gerentes" in resp.json().get("detail", "").lower()


@pytest.mark.django_db
def test_get_list_success(client_autenticado_comum, usuario_comum):
    Categoria.objects.create(nome="Cat Lista OK", tipo="E", created_by=usuario_comum)
    resp = client_autenticado_comum.get(reverse("categoria-list-create"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "results" in body
    assert "count" in body
    assert body["count"] >= 1
    nomes = {r["nome"] for r in body["results"]}
    assert "Cat Lista OK" in nomes


@pytest.mark.django_db
def test_get_list_scope_isolation(
    client_autenticado_comum, usuario_comum, outro_usuario_comum
):
    Categoria.objects.create(nome="SoDoOutro", tipo="S", created_by=outro_usuario_comum)
    resp = client_autenticado_comum.get(reverse("categoria-list-create"))
    assert resp.status_code == status.HTTP_200_OK
    nomes = {r["nome"] for r in resp.json()["results"]}
    assert "SoDoOutro" not in nomes


@pytest.mark.django_db
def test_get_list_pagination(client_autenticado_comum, usuario_comum):
    for i in range(11):
        Categoria.objects.create(
            nome=f"PagCat{i:02d}", tipo="E", created_by=usuario_comum
        )
    resp = client_autenticado_comum.get(reverse("categoria-list-create"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["count"] >= 11
    assert len(body["results"]) == 10
    assert body["next"] is not None


@pytest.mark.django_db
def test_get_list_filter_tipo(client_autenticado_comum, usuario_comum):
    Categoria.objects.create(nome="SoEntrada", tipo="E", created_by=usuario_comum)
    Categoria.objects.create(nome="SoSaida", tipo="S", created_by=usuario_comum)
    resp = client_autenticado_comum.get(
        reverse("categoria-list-create"), {"tipo": "E"}
    )
    assert resp.status_code == status.HTTP_200_OK
    tipos = {r["tipo"] for r in resp.json()["results"]}
    assert tipos == {"E"}


@pytest.mark.django_db
def test_get_list_empty(client_autenticado_sem_categorias):
    """Lista vazia: utilizador criado sem categorias iniciais (signal desligado)."""
    resp = client_autenticado_sem_categorias.get(reverse("categoria-list-create"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["count"] == 0
    assert body["results"] == []


@pytest.mark.django_db
def test_get_detail_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("categoria-retrieve-update-destroy", kwargs={"pk": 1}))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_detail_forbidden_subject_header(
    client_autenticado_comum, outro_usuario_comum
):
    resp = client_autenticado_comum.get(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": 1}),
        HTTP_X_FINANCAS_SUBJECT_USER=str(outro_usuario_comum.pk),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_detail_success(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.create(
        nome="DetalheCat", tipo="S", descricao="d1", created_by=usuario_comum
    )
    resp = client_autenticado_comum.get(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat.pk})
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["id"] == cat.pk
    assert body["nome"] == "DetalheCat"
    assert body["tipo"] == "S"
    assert body["descricao"] == "d1"


@pytest.mark.django_db
def test_get_detail_not_found(client_autenticado_comum):
    resp = client_autenticado_comum.get(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": 999_999})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_detail_scope_isolation(
    client_autenticado_comum, outro_usuario_comum, usuario_comum
):
    cat_outro = Categoria.objects.create(
        nome="IdorCat", tipo="E", created_by=outro_usuario_comum
    )
    resp = client_autenticado_comum.get(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat_outro.pk})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_post_create_unauthenticated():
    client = APIClient()
    resp = client.post(
        reverse("categoria-list-create"),
        {"nome": "X", "tipo": "E"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_create_validation_required(client_autenticado_comum):
    resp = client_autenticado_comum.post(
        reverse("categoria-list-create"), {}, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    body = resp.json()
    assert "nome" in body or "tipo" in body


@pytest.mark.django_db
def test_post_create_success(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.post(
        reverse("categoria-list-create"),
        {"nome": "NovaCatAPI", "tipo": "E", "descricao": "via teste"},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["nome"] == "NovaCatAPI"
    assert body["tipo"] == "E"
    assert Categoria.objects.filter(
        nome="NovaCatAPI", created_by=usuario_comum
    ).exists()


@pytest.mark.django_db
def test_post_create_validation_tipo_invalido(client_autenticado_comum):
    """Valor de ``tipo`` fora das escolhas do modelo → 400 (serializer)."""
    resp = client_autenticado_comum.post(
        reverse("categoria-list-create"),
        {"nome": "CatTipoRuim", "tipo": "X"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_put_update_success(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.create(nome="Antes", tipo="E", created_by=usuario_comum)
    resp = client_autenticado_comum.put(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat.pk}),
        {"nome": "Depois", "tipo": "S", "descricao": "", "icone": None},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    cat.refresh_from_db()
    assert cat.nome == "Depois"
    assert cat.tipo == "S"


@pytest.mark.django_db
def test_put_update_not_found(client_autenticado_comum, usuario_comum):
    """PUT em PK inexistente (no escopo do utilizador)."""
    Categoria.objects.create(nome="Hold", tipo="E", created_by=usuario_comum)
    resp = client_autenticado_comum.put(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": 999_999}),
        {"nome": "X", "tipo": "E", "descricao": "", "icone": None},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_put_update_scope_isolation(
    client_autenticado_comum, outro_usuario_comum, usuario_comum
):
    cat = Categoria.objects.create(nome="OutroDono", tipo="E", created_by=outro_usuario_comum)
    resp = client_autenticado_comum.put(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat.pk}),
        {"nome": "Hack", "tipo": "S", "descricao": "", "icone": None},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    cat.refresh_from_db()
    assert cat.nome == "OutroDono"


@pytest.mark.django_db
def test_patch_partial_update(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.create(nome="PatchMe", tipo="E", created_by=usuario_comum)
    resp = client_autenticado_comum.patch(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat.pk}),
        {"descricao": "só desc"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    cat.refresh_from_db()
    assert cat.descricao == "só desc"
    assert cat.nome == "PatchMe"


@pytest.mark.django_db
def test_delete_unauthenticated():
    client = APIClient()
    resp = client.delete(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": 1})
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_forbidden_subject_header(
    client_autenticado_comum, outro_usuario_comum, usuario_comum
):
    cat = Categoria.objects.create(nome="DelBlock", tipo="E", created_by=usuario_comum)
    resp = client_autenticado_comum.delete(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat.pk}),
        HTTP_X_FINANCAS_SUBJECT_USER=str(outro_usuario_comum.pk),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_success(client_autenticado_comum, usuario_comum):
    cat = Categoria.objects.create(nome="VaiSumir", tipo="E", created_by=usuario_comum)
    pk = cat.pk
    resp = client_autenticado_comum.delete(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": pk})
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "sucesso" in resp.json().get("detail", "").lower()
    assert not Categoria.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_delete_not_found(client_autenticado_comum):
    resp = client_autenticado_comum.delete(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": 999_999})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_scope_isolation(
    client_autenticado_comum, outro_usuario_comum, usuario_comum
):
    cat = Categoria.objects.create(
        nome="NaoApagar", tipo="S", created_by=outro_usuario_comum
    )
    resp = client_autenticado_comum.delete(
        reverse("categoria-retrieve-update-destroy", kwargs={"pk": cat.pk})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert Categoria.objects.filter(pk=cat.pk).exists()
