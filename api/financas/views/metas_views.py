from financas.models import Meta
from financas.serializers import MetaSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status   

class MetaListCreateView(generics.ListCreateAPIView):
    serializer_class = MetaSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'prioridade': ['exact'],           # ?prioridade=R ou ?prioridade=M ou ?prioridade=L
        'data_meta': ['gte', 'lte'],      # ?data_meta__gte=2025-01-01
        'concluida': ['exact'],           # ?concluida=True ou ?concluida=False
    }
    ordering_fields = [
        'nome',
        'data_meta',
        'prioridade',
        'concluida',
        'created_at',
        'created_by'
    ]
    ordering = ['-data_meta']  # padrão
    def get_queryset(self):
        return Meta.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MetaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MetaSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Meta.objects.filter(created_by=self.request.user)
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Meta removida com sucesso."},
            status=status.HTTP_200_OK
        )


"""
    Modo de usar:
    Trazer todas as metas:
    /api/metas/
    Criar uma nova meta:
    /api/metas/
    {
        "nome": "Meta de Renda",
        "valor": 1000.00,
        "data_meta": "2025-01-01"
    }
    Atualizar uma meta:
    /api/metas/1/
    {
        "nome": "Meta de Renda",
        "valor": 1000.00,
        "data_meta": "2025-01-01"
    }
    Remover uma meta:
    /api/metas/1/
    {
        "nome": "Meta de Renda",
        "valor": 1000.00,
        "data_meta": "2025-01-01"
    }   
"""