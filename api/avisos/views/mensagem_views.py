from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from avisos.models import Mensagem
from avisos.serializers import MensagemSerializer


class MensagemListCreateView(generics.ListCreateAPIView):
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "lido": ["exact"],
        "star": ["exact"],
        "destino": ["exact"],
        "remetente": ["exact"],
    }

    def get_queryset(self):
        user = self.request.user
        return Mensagem.objects.filter(Q(remetente=user) | Q(destino=user))

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(remetente=self.request.user)


class MensagemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Mensagem.objects.filter(Q(remetente=user) | Q(destino=user))

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Mensagem removida com sucesso."},
            status=status.HTTP_200_OK,
        )
