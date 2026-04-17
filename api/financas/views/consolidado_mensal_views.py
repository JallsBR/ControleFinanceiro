from app.financas_subject import get_financas_subject_user
from financas.models import ConsolidadoMensal
from financas.serializers import ConsolidadoMensalSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import status

CONSOLIDADOS_ULTIMOS_MESES = 12


class ConsolidadoMensalListCreateView(generics.ListCreateAPIView):
    serializer_class = ConsolidadoMensalSerializer
    permission_classes = [IsAuthenticated]
    # Filtros e ordenação
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'ano': ['exact'],           # ?ano=2025
        'mes': ['exact'],           # ?mes=1
        'total_entradas': ['exact'],           # ?total_entradas=1000.00
        'total_saidas': ['exact'],           # ?total_saidas=1000.00
    }
    ordering_fields = [
        'ano',
        'mes',
        'total_entradas',
        'total_saidas',
    ]
    ordering = ['-ano', '-mes']  # padrão: mais recentes primeiro

    def get_queryset(self):
        return ConsolidadoMensal.objects.filter(
            created_by=get_financas_subject_user(self.request)
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-ano', '-mes')[:CONSOLIDADOS_ULTIMOS_MESES]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def perform_create(self, serializer):
        serializer.save(created_by=get_financas_subject_user(self.request))


class ConsolidadoMensalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConsolidadoMensalSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ConsolidadoMensal.objects.filter(
            created_by=get_financas_subject_user(self.request)
        )
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {"detail": "Consolidado Mensal removido com sucesso."},
            status=status.HTTP_200_OK
        )


"""
Modo de Uso
    Trazer todos os consolidados mensais:
    /api/consolidados-mensais/
    Criar um novo consolidado mensal:
    /api/consolidados-mensais/
    {
        "ano": 2025,
        "mes": 1,
        "total_entradas": 1000.00,
        "total_saidas": 1000.00
    }
    Atualizar um consolidado mensal:
    /api/consolidados-mensais/1/
    {
        "ano": 2025,
        "mes": 1,
        "total_entradas": 1000.00,
        "total_saidas": 1000.00
    }
    Remover um consolidado mensal:
    /api/consolidados-mensais/1/
    {
        "ano": 2025,
        "mes": 1,
        "total_entradas": 1000.00,
        "total_saidas": 1000.00
    }
"""