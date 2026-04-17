from financas.models import Icone
from financas.serializers import IconeSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status   

class IconeListCreateView(generics.ListCreateAPIView):
    queryset = Icone.objects.all()
    serializer_class = IconeSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'categoria_visual': ['exact'],
        'nome': ['exact'],
        'classe_css': ['exact'],
    }
    ordering_fields = [
        'nome',
        'classe_css',
        'categoria_visual',
    ]
    ordering = ['nome']
    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Apenas administradores podem criar ícones.")
        
        serializer.save(created_by=self.request.user)


class IconeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Icone.objects.all()
    serializer_class = IconeSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        obj = get_object_or_404(Icone, pk=self.kwargs["pk"])
        # Se for UPDATE ou DELETE, verifica se é o criador
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            if obj.created_by != self.request.user:
                raise PermissionDenied(
                    "Você não tem permissão para alterar ou remover este ícone."
                )
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Ícone removido com sucesso."},
            status=status.HTTP_200_OK
        )

"""
Modo de usar:

    Trazer todos os ícones:
    /api/icones/
    
    Criar um novo ícone:
    /api/icones/
    {
        "nome": "Dinheiro",
        "classe_css": "pi pi-wallet",
        "categoria_visual": "Financeiro"
    }
    
    Atualizar um ícone:
    /api/icones/1/
    {
        "nome": "Dinheiro",
        "classe_css": "pi pi-wallet",
        "categoria_visual": "Financeiro"
    }
    
    Remover um ícone:
    /api/icones/1/
    {
        "nome": "Dinheiro",
        "classe_css": "pi pi-wallet",
        "categoria_visual": "Financeiro"
    }
    
"""