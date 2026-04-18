from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from avisos.models import SolicitacaoConsultoria
from avisos.serializers import SolicitacaoConsultoriaSerializer
from users.models import Consultoria


class SolicitacaoConsultoriaListCreateView(generics.ListCreateAPIView):
    serializer_class = SolicitacaoConsultoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        "aceito": ["exact"],
        "usuario": ["exact"],
        "consultor": ["exact"],
    }
    search_fields = ("usuario__username", "usuario__email")

    def get_queryset(self):
        user = self.request.user
        return SolicitacaoConsultoria.objects.filter(
            Q(usuario=user) | Q(consultor=user)
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class SolicitacaoConsultoriaRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = SolicitacaoConsultoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SolicitacaoConsultoria.objects.filter(
            Q(usuario=user) | Q(consultor=user)
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def perform_destroy(self, instance):
        if instance.consultor_id != self.request.user.id:
            raise PermissionDenied(
                "Só o consultor destinatário pode recusar e eliminar este pedido."
            )
        if instance.aceito:
            Consultoria.objects.filter(
                gerente_id=instance.consultor_id,
                cliente_id=instance.usuario_id,
                status=Consultoria.Status.ATIVA,
            ).update(status=Consultoria.Status.ENCERRADA)
        super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        era_aceito = instance.aceito
        self.perform_destroy(instance)
        detail = (
            "Vínculo encerrado e pedido removido com sucesso."
            if era_aceito
            else "Solicitação recusada e removida com sucesso."
        )
        return Response({"detail": detail}, status=status.HTTP_200_OK)
