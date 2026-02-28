from financas.models import Categoria
from financas.serializers import CategoriaSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status




class CategoriaListCreateView(generics.ListCreateAPIView):
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'tipo': ['exact'],           # ?tipo=E ou ?tipo=S
    }
    ordering_fields = [
        'nome',
        'tipo',
        'created_at',
        'last_updated'
    ]
    ordering = ['nome']  # padrão
    def get_queryset(self):
        return Categoria.objects.filter(
            created_by=self.request.user
        )
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoriaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Categoria.objects.filter(
            created_by=self.request.user
        )
    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Categoria removida com sucesso."},
            status=status.HTTP_200_OK
        )
"""
    Trazer só entradas:
    /api/categorias/?tipo=E

    Trazer só saídas:
    /api/categorias/?tipo=S

    Ordenar por nome crescente:
    /api/categorias/?ordering=nome

    Ordenar por nome decrescente:
    /api/categorias/?ordering=-nome
    
    Data maior ou igual:
    /api/categorias/?created_at__gte=2025-01-01

"""