"""Tipo 1 e 2 — listagem e detalhe admin de utilizadores (/api/v1/auth/admin/users)."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Assinatura, User


@pytest.mark.django_db
def test_get_list_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("admin_users"))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_list_forbidden(client_autenticado_comum):
    resp = client_autenticado_comum.get(reverse("admin_users"))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_list_success(client_autenticado_staff, usuario_comum, usuario_staff):
    resp = client_autenticado_staff.get(reverse("admin_users"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "results" in body
    ids = {row["id"] for row in body["results"]}
    assert usuario_comum.id in ids
    assert usuario_staff.id in ids
    primeiro = next(r for r in body["results"] if r["id"] == usuario_comum.id)
    assert "email" in primeiro and "username" in primeiro
    assert "assinatura" in primeiro


@pytest.mark.django_db
def test_get_list_pagination(client_autenticado_staff, usuario_staff):
    for i in range(15):
        User.objects.create_user(
            username=f"pag_user_{i}",
            email=f"pag{i}@example.com",
            password="SenhaSegura123!",
        )
    resp = client_autenticado_staff.get(reverse("admin_users"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["count"] >= 16
    assert "next" in body and body["next"] is not None
    assert len(body["results"]) == 10


@pytest.mark.django_db
def test_get_list_filter_username(
    client_autenticado_staff, usuario_comum, usuario_staff
):
    resp = client_autenticado_staff.get(
        reverse("admin_users"), {"username": usuario_comum.username[:4]}
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    for row in body["results"]:
        assert usuario_comum.username[:4].lower() in row["username"].lower()


@pytest.mark.django_db
def test_get_list_filter_plano_premium(client_autenticado_staff):
    alvo = User.objects.create_user(
        username="premium_only",
        email="premium_only@example.com",
        password="SenhaSegura123!",
    )
    # post_save já criou Assinatura (comum); só ajustamos o plano para o filtro.
    Assinatura.objects.filter(user=alvo).update(
        plano=Assinatura.Plano.PREMIUM,
        status=Assinatura.Status.ATIVA,
    )
    resp = client_autenticado_staff.get(
        reverse("admin_users"),
        {"plano": "premium", "username": "premium_only"},
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["count"] == 1
    assert body["results"][0]["id"] == alvo.id
    assert body["results"][0]["assinatura"] == "premium"


@pytest.mark.django_db
def test_get_list_empty_filter_sem_match(client_autenticado_staff, usuario_staff):
    resp = client_autenticado_staff.get(
        reverse("admin_users"), {"username": "xyz_nao_existe_999"}
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["results"] == []
    assert body["count"] == 0


@pytest.mark.django_db
def test_get_detail_unauthenticated():
    client = APIClient()
    resp = client.get(reverse("admin_user_detail", kwargs={"pk": 1}))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_detail_forbidden(client_autenticado_comum, usuario_comum):
    resp = client_autenticado_comum.get(
        reverse("admin_user_detail", kwargs={"pk": usuario_comum.pk})
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_detail_success(client_autenticado_staff, usuario_comum):
    resp = client_autenticado_staff.get(
        reverse("admin_user_detail", kwargs={"pk": usuario_comum.pk})
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == usuario_comum.id


@pytest.mark.django_db
def test_get_detail_not_found(client_autenticado_staff):
    resp = client_autenticado_staff.get(
        reverse("admin_user_detail", kwargs={"pk": 999_999})
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_admin_user_detail_success(
    client_autenticado_staff, usuario_comum, usuario_staff
):
    resp = client_autenticado_staff.patch(
        reverse("admin_user_detail", kwargs={"pk": usuario_comum.pk}),
        {"first_name": "PeloStaff"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    usuario_comum.refresh_from_db()
    assert usuario_comum.first_name == "PeloStaff"


@pytest.mark.django_db
def test_patch_admin_user_detail_not_found(client_autenticado_staff):
    resp = client_autenticado_staff.patch(
        reverse("admin_user_detail", kwargs={"pk": 999_999}),
        {"first_name": "X"},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_detail_usuario_comum_nao_acessa_outro(
    client_autenticado_comum, usuario_comum, outro_usuario_comum
):
    """Utilizador sem staff não deve obter detalhe admin de outro utilizador."""
    resp = client_autenticado_comum.get(
        reverse("admin_user_detail", kwargs={"pk": outro_usuario_comum.pk})
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
