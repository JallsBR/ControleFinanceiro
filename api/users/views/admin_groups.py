from collections import defaultdict

from django.contrib.auth.models import Group, Permission
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import AdminGroupListSerializer, AdminGroupWriteSerializer


def admin_groups_list_queryset():
    """Queryset para listagem/detalhe de grupo com contagens.

    Não fazemos prefetch de membros com ``LIMIT`` no inner queryset: em MySQL/MariaDB
    isso costuma gerar subconsulta inválida (500). Os nomes vêm do serializer com
    ``user_set`` limitado a poucas linhas por grupo.
    """
    return Group.objects.annotate(
        permissions_count=Count("permissions"),
        user_count=Count("user", distinct=True),
    )


def build_permission_tree():
    """
    Árvore app → modelo → permissões, com allPermissionIds para seleção em massa no front.
    """
    perms = (
        Permission.objects.select_related("content_type").order_by(
            "content_type__app_label",
            "content_type__model",
            "codename",
        )
    )
    nested = defaultdict(lambda: defaultdict(list))
    for p in perms:
        app = p.content_type.app_label
        model = p.content_type.model
        nested[app][model].append(
            {
                "id": p.id,
                "codename": p.codename,
                "name": p.name,
            }
        )
    tree = []
    for app in sorted(nested.keys()):
        model_nodes = []
        app_ids = []
        for model in sorted(nested[app].keys()):
            plist = nested[app][model]
            ids = [x["id"] for x in plist]
            app_ids.extend(ids)
            model_nodes.append(
                {
                    "key": f"{app}.{model}",
                    "label": model,
                    "allPermissionIds": ids,
                    "permissions": plist,
                }
            )
        tree.append(
            {
                "key": app,
                "label": app,
                "allPermissionIds": app_ids,
                "children": model_nodes,
            }
        )
    return tree


class AdminPermissionTreeView(APIView):
    """Árvore de permissões (read-only) para o diálogo admin."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({"tree": build_permission_tree()})


class AdminGroupOptionsView(APIView):
    """Lista compacta id + nome para selects (sem paginação)."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        rows = list(
            Group.objects.order_by("name").values("id", "name")[:500]
        )
        return Response(rows)


class AdminGroupListCreateView(generics.ListCreateAPIView):
    """
    Lista paginada de grupos (GET) e criação (POST).
    Query: name (icontains).
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        qs = admin_groups_list_queryset().order_by("name")
        if v := (self.request.query_params.get("name") or "").strip():
            qs = qs.filter(name__icontains=v)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminGroupWriteSerializer
        return AdminGroupListSerializer

    def create(self, request, *args, **kwargs):
        ser = AdminGroupWriteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        group = Group.objects.create(**ser.validated_data)
        group = admin_groups_list_queryset().filter(pk=group.pk).first()
        return Response(
            AdminGroupListSerializer(group).data,
            status=status.HTTP_201_CREATED,
        )


class AdminGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalhe, renomear (PATCH) ou apagar (DELETE) grupo."""

    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = admin_groups_list_queryset().order_by("name")

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return AdminGroupWriteSerializer
        return AdminGroupListSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        obj = admin_groups_list_queryset().filter(pk=instance.pk).first()
        return Response(AdminGroupListSerializer(obj).data)


class AdminGroupPermissionsView(APIView):
    """Ler ou substituir permissões de um grupo (lista de IDs)."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        return Response(
            {"permission_ids": list(group.permissions.values_list("pk", flat=True))}
        )

    def put(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        ids = request.data.get("permission_ids")
        if ids is None or not isinstance(ids, list):
            return Response(
                {"permission_ids": ["Envie uma lista permission_ids."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        uniq = []
        seen = set()
        for i in ids:
            try:
                pid = int(i)
            except (TypeError, ValueError):
                return Response(
                    {"permission_ids": ["Cada id tem de ser um número inteiro."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if pid not in seen:
                seen.add(pid)
                uniq.append(pid)
        perms = Permission.objects.filter(pk__in=uniq)
        if perms.count() != len(uniq):
            return Response(
                {"permission_ids": ["Um ou mais IDs de permissão são inválidos."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        group.permissions.set(perms)
        return Response(
            {"permission_ids": list(group.permissions.values_list("pk", flat=True))}
        )
