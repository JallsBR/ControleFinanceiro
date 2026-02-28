from financas.models import Movimentacao
from financas.serializers import MovimentacaoSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status

class MovimentacaoListCreateView(generics.ListCreateAPIView):
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'tipo': ['exact'],           # ?tipo=E ou ?tipo=S
        'data': ['gte', 'lte'],      # ?data__gte=2025-01-01
        'categoria': ['exact'],      # ?categoria=1
    }
    ordering_fields = [
        'valor',
        'data',
        'categoria',
        'created_by'
    ]
    ordering = ['-data']  # padrão
    def get_queryset(self):
        return Movimentacao.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MovimentacaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Movimentacao.objects.filter(created_by=self.request.user)
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Movimentação removida com sucesso."},
            status=status.HTTP_200_OK
        )


"""
    Trazer só entradas:
    /api/movimentacoes/?tipo=E
    
    Trazer só saídas:
    /api/movimentacoes/?tipo=S

    Ordenar por valor crescente:
    /api/movimentacoes/?ordering=valor

    Ordenar por valor decrescente:
    /api/movimentacoes/?ordering=-valor
    
    Data maior ou igual:
    /api/movimentacoes/?data__gte=2025-01-01
"""