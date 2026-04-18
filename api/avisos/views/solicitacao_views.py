from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.financas_subject import get_financas_subject_user
from app.consultoria_subject import request_user_pode_atuar_como_consultor_da_solicitacao
from avisos.models import SolicitacaoConsultoria
from avisos.serializers import SolicitacaoConsultoriaSerializer
from users.models import Consultoria


class SolicitacaoConsultoriaListCreateView(generics.ListCreateAPIView):
    serializer_class = SolicitacaoConsultoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        "usuario": ["exact"],
        "consultor": ["exact"],
    }
    search_fields = ("usuario__username", "usuario__email")

    def get_queryset(self):
        subject = get_financas_subject_user(self.request)
        return SolicitacaoConsultoria.objects.filter(
            Q(usuario=subject) | Q(consultor=subject)
        )

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        estado = (self.request.query_params.get("estado") or "").strip().lower()
        if estado == "pendente":
            return qs.filter(aceito=False)
        if estado == "aceito":
            return qs.filter(aceito=True, vinculo_encerrado=False)
        if estado == "encerrada":
            return qs.filter(aceito=True, vinculo_encerrado=True)
        raw_aceito = self.request.query_params.get("aceito")
        if raw_aceito is not None:
            s = str(raw_aceito).strip().lower()
            if s in ("false", "0", "no"):
                return qs.filter(aceito=False)
            if s in ("true", "1", "yes"):
                return qs.filter(aceito=True)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(usuario=get_financas_subject_user(self.request))


class SolicitacaoConsultoriaRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = SolicitacaoConsultoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject = get_financas_subject_user(self.request)
        return SolicitacaoConsultoria.objects.filter(
            Q(usuario=subject) | Q(consultor=subject)
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def perform_destroy(self, instance):
        if not request_user_pode_atuar_como_consultor_da_solicitacao(
            self.request, instance.consultor_id
        ):
            raise PermissionDenied(
                "Só o consultor destinatário pode recusar e eliminar este pedido."
            )
        if instance.vinculo_encerrado:
            super().perform_destroy(instance)
            return
        if instance.aceito:
            Consultoria.objects.filter(
                gerente_id=instance.consultor_id,
                cliente_id=instance.usuario_id,
                status=Consultoria.Status.ATIVA,
            ).update(status=Consultoria.Status.ENCERRADA)
            SolicitacaoConsultoria.objects.filter(pk=instance.pk).update(
                vinculo_encerrado=True
            )
            return
        super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        era_encerrada = instance.vinculo_encerrado
        era_aceito = instance.aceito
        self.perform_destroy(instance)
        if era_encerrada:
            detail = "Solicitação encerrada eliminada com sucesso."
        elif era_aceito:
            detail = (
                "Consultoria encerrada. A solicitação ficou registada como encerrada."
            )
        else:
            detail = "Solicitação recusada e removida com sucesso."
        return Response({"detail": detail}, status=status.HTTP_200_OK)
