from financas.models import MovimentacaoRecorrente
from financas.serializers import MovimentacaoRecorrenteSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status


class MovimentacaoRecorrenteListCreateView(generics.ListCreateAPIView):
    serializer_class = MovimentacaoRecorrenteSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'tipo': ['exact'],           # ?tipo=E ou ?tipo=S
        'ativa': ['exact'],          # ?ativa=true
        'frequencia': ['exact'],     # ?frequencia=M
        'data_inicio': ['gte', 'lte'],  # ?data_inicio__gte=2025-01-01
        'data_fim': ['gte', 'lte'],
    }
    ordering_fields = [
        'data_inicio',
        'valor',
        'frequencia',
        'ativa'
    ]
    ordering = ['-data_inicio']  # padrão
    def get_queryset(self):
        return MovimentacaoRecorrente.objects.filter(
            created_by=self.request.user
        )
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



class MovimentacaoRecorrenteRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MovimentacaoRecorrenteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MovimentacaoRecorrente.objects.filter(
            created_by=self.request.user
        )

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Movimentação Recorrente removida com sucesso."},
            status=status.HTTP_200_OK
        )

"""
    Trazer só entradas:
    /api/movimentacoes-recorrentes/?tipo=E

    Só saídas ativas:
    /api/movimentacoes-recorrentes/?tipo=S&ativa=true

    Ordenar por valor crescente:
    /api/movimentacoes-recorrentes/?ordering=valor

    Ordenar por valor decrescente:
    /api/movimentacoes-recorrentes/?ordering=-valor

    Data maior ou igual:
    /api/movimentacoes-recorrentes/?data_inicio__gte=2025-01-01

    Data menor ou igual:
    /api/movimentacoes-recorrentes/?data_inicio__lte=2025-01-01

    Data maior ou igual e menor ou igual:
    /api/movimentacoes-recorrentes/?data_inicio__gte=2025-01-01&data_inicio__lte=2025-01-01
    
"""