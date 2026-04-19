from django.db.models import Q
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import AdminUserListSerializer, AdminUserUpdateSerializer


class AdminUserListView(ListAPIView):
    """
    Listagem paginada de usuários com dados de assinatura (staff).
    Query: page, username, email, nome, plano (comum|premium),
    tipo_usuario (superuser | staff | comum), ordering (DRF).
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminUserListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "assinatura__plano",
    ]
    ordering = ["id"]

    def get_queryset(self):
        qs = User.objects.select_related("assinatura").prefetch_related("groups")
        p = self.request.query_params

        if v := (p.get("username") or "").strip():
            qs = qs.filter(username__icontains=v)
        if v := (p.get("email") or "").strip():
            qs = qs.filter(email__icontains=v)
        if v := (p.get("nome") or "").strip():
            qs = qs.filter(
                Q(first_name__icontains=v)
                | Q(last_name__icontains=v)
            )
        if v := (p.get("plano") or "").strip():
            if v in ("comum", "premium"):
                qs = qs.filter(assinatura__plano=v)

        if v := (p.get("tipo_usuario") or "").strip():
            if v == "superuser":
                qs = qs.filter(is_superuser=True)
            elif v == "staff":
                qs = qs.filter(is_staff=True, is_superuser=False)
            elif v == "comum":
                qs = qs.filter(is_staff=False, is_superuser=False)

        return qs


class AdminUserDetailView(RetrieveUpdateAPIView):
    """
    GET/PATCH de um utilizador (staff). PATCH aceita plano da assinatura (comum|premium).
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.select_related("assinatura").prefetch_related("groups")
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return AdminUserUpdateSerializer
        return AdminUserListSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = (
            User.objects.select_related("assinatura")
            .prefetch_related("groups")
            .get(pk=serializer.instance.pk)
        )
        return Response(
            AdminUserListSerializer(instance, context={"request": request}).data
        )
