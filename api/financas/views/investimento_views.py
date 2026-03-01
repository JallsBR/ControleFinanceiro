from financas.models import Investimento
from financas.serializers import InvestimentoSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status

class InvestimentoListCreateView(generics.ListCreateAPIView):
    serializer_class = InvestimentoSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'ativo': ['exact'],           # ?ativo=True ou ?ativo=False
    }
    ordering_fields = [
        'valor',
        'created_by'
    ]
    ordering = ['-created_at']  # padrão
    def get_queryset(self):
        return Investimento.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InvestimentoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvestimentoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Investimento.objects.filter(created_by=self.request.user)
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Investimento removido com sucesso."},
            status=status.HTTP_200_OK
        )


"""
    Trazer só ativos:
    /api/investimentos/?ativo=True

    Trazer só inativos:
    /api/investimentos/?ativo=False

    Ordenar por valor crescente:
    /api/investimentos/?ordering=valor
"""