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
        # ?ativo=True ou ?ativo=False
        'ativo': ['exact'],
        # ?tipo=CDB, ?tipo=FII, etc.
        'tipo': ['exact'],
        # ?data_aplicacao=2025-01-01, ou usando sufixos: data_aplicacao__gte, data_aplicacao__lte
        'data_aplicacao': ['exact', 'gte', 'lte'],
        # ?data_vencimento=2025-12-31, ou data_vencimento__gte / __lte
        'data_vencimento': ['exact', 'gte', 'lte'],
        # ?valor_inicial=1000, ou valor_inicial__gte / __lte
        'valor_inicial': ['exact', 'gte', 'lte'],
        # ?taxa_rendimento=10, ou taxa_rendimento__gte / __lte
        'taxa_rendimento': ['exact', 'gte', 'lte'],
    }
    ordering_fields = [
        'data_aplicacao',
        'data_vencimento',
        'valor_inicial',
        'taxa_rendimento',
        'created_at',
        
    ]
    ordering = ['-created_at']  # padrão
    def get_queryset(self):
        return Investimento.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            usuario=self.request.user,
            created_by=self.request.user,
        )


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
    Exemplos de filtros e ordenação para investimentos:

    - Trazer só ativos:
      /api/v1/financas/investimentos/?ativo=True

    - Trazer só inativos:
      /api/v1/financas/investimentos/?ativo=False

    - Filtrar por tipo (ex: CDB):
      /api/v1/financas/investimentos/?tipo=CDB

    - Filtrar por período de aplicação:
      /api/v1/financas/investimentos/?data_aplicacao__gte=2025-01-01&data_aplicacao__lte=2025-12-31

    - Filtrar por valor inicial mínimo:
      /api/v1/financas/investimentos/?valor_inicial__gte=1000

    - Ordenar por data de aplicação crescente:
      /api/v1/financas/investimentos/?ordering=data_aplicacao

    - Ordenar por valor inicial decrescente:
      /api/v1/financas/investimentos/?ordering=-valor_inicial
"""